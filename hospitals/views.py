from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.list import MultipleObjectMixin
from django.core.mail import send_mail
from django.views import View
from .forms import *
from accounts.forms import *
from django.urls import reverse, reverse_lazy
from django.template.loader import get_template
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from . import views
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.contrib.auth import get_user_model
from django.conf import settings
from accounts.models import User, Hospital
from .models import Document, Payment, Inspection, License, Schedule, Appraisal
from django.db.models import Q  
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from io import BytesIO
from django.utils.decorators import method_decorator
import uuid
from django.db.models.functions import Coalesce
from itertools import chain
from django.db.models import Max, Value, CharField
from django.contrib.auth.mixins import LoginRequiredMixin
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import landscape, portrait
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.views.generic.detail import SingleObjectMixin
from itertools import chain




User = get_user_model()

class StaffRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role == 'Hospital':
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(StaffRequiredMixin, self).dispatch(request,
            *args, **kwargs)


# class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)







@login_required
def hospitals_dashboard(request):
     hospitals = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=request.user, application_status=8)
     license = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=request.user, application_status=8).count()

     user = request.user
     # Fetch application numbers from Document and License models
     document_applications = Document.objects.filter(hospital_name__hospital_admin=user)
     license_application_numbers = License.objects.filter(hospital_name__hospital_admin=user).values_list("application_no", flat=True)
     # Filter Document applications that are not in License model
     pending_license_applications = document_applications.exclude(application_no__in=license_application_numbers).count()

     

     hospital = Hospital.objects.filter(hospital_admin=request.user)
     object = hospital[0]

     context = {
          'hospitals': hospitals,
          'hospital': hospital,
          'object': object,
          'license': license,
          'pending_license_applications': pending_license_applications
     }
     return render(request, 'hospitals/hospitals_dashboard.html', context)




class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class MyApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_tables.html"
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user

        # Fetch related data from models with annotations
        models = [
            (Document, "Document"),
            (Payment, "Payment"),
            (Schedule, "Schedule"),
            (Inspection, "Inspection"),
            (License, "License"),
            (Appraisal, "Internship"),
        ]
        querysets = [
            model.objects.filter(hospital_name__hospital_admin=user)
            .annotate(model_name=Value(name, output_field=CharField()))
            for model, name in models
        ]

        combined_qs = list(chain(*querysets))

        # Priority mapping for sorting
        model_priority = {
            "Document": 6,
            "Payment": 5,
            "Schedule": 4,
            "Inspection": 3,
            "Internship": 2,
             "License": 1,
        }

        # Sorting and grouping
        combined_qs.sort(
            key=lambda obj: (
                obj.application_no,
                model_priority.get(obj.model_name, 0),
            )
        )

        most_recent = {}
        for obj in combined_qs:
            if obj.application_no not in most_recent:
                most_recent[obj.application_no] = obj

        return list(most_recent.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = self.get_queryset()
        hospitals = Hospital.objects.filter(hospital_admin=self.request.user)
        context["applications"] = applications
        context["hospitals"] = hospitals

        # Safely add hospital_name
        if applications:
            context["hospital_name"] = applications[0].hospital_name
        else:
            context["hospital"] = hospitals

        return context


class NewHospitalProfileDetails(DetailView, LoginRequiredMixin):
    template_name = "hospitals/hospital_profile_details.html"
    model = Hospital


class UpdateHospitalProfileDetails(SuccessMessageMixin, UpdateView, LoginRequiredMixin):
    template_name = "hospitals/update_hospital_profile.html"
    success_message = "%(hospital)s Hospital Profile Update Successful"
    
    def get_object(self, queryset=None):
        """Get the hospital profile object based on the primary key."""
        return get_object_or_404(Hospital, id=self.kwargs.get("pk"))
    
    def get_success_message(self, cleaned_data):
        return self.success_message % {
            "hospital": self.object.hospital_name,
        }

    def get(self, request, *args, **kwargs):
        """Render the update form with the hospital and associated user data."""
        hospital = self.get_object()
        user = hospital.hospital_admin

        context = {
            "object": hospital,
            "form": HospitalProfileModelForm(instance=hospital),
            "user_form": UserUpdateForm(instance=user),
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for updating the hospital profile."""
        hospital = self.get_object()
        user = hospital.hospital_admin

        form = HospitalProfileModelForm(request.POST, instance=hospital)
        user_form = UserUpdateForm(request.POST, instance=user)

        if form.is_valid() and user_form.is_valid():
            # Update hospital profile
            self.object = form.save(commit=False)  # Set self.object explicitly
            if self.object.application_status <= 2:
                self.object.application_status = 2
            self.object.save()

            # Update user profile
            user_instance = user_form.save(commit=False)
            user_instance.is_active = True
            user_instance.hospital = True
            user_instance.save()

            messages.success(request, self.get_success_message(form.cleaned_data))
            return redirect(hospital.get_absolute_url())
        
        # Handle invalid form submission
        messages.error(request, "Hospital Profile Update Failed.")
        return render(request, self.template_name, {
            "object": hospital,
            "form": form,
            "user_form": user_form,
        })



class UpdateHospitalProfileDetails2 (LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    user_form = UserUpdateForm
    form = HospitalProfileModelForm
    template_name = "hospitals/update_hospital_profile.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        hospital_profile = Hospital.objects.get(id=pk)
        return hospital_profile
   
    def get(self, request, *args, **kwargs):
        context = {}
        obj = self.get_object()
        user = User.objects.filter(email=obj.hospital_admin.email).first()
        print ("User:", user)
        if obj and user is not None:
            form = HospitalProfileModelForm(instance=obj)
            user_form = UserUpdateForm(instance=user)
            context['object'] = obj
            context['form'] = form
            context['user_form'] = user_form
        
        return render(request, self.template_name, context)
  

    success_message = "%(hospital_admin)s  Hospital Profile Update Successful"
    
    def get_success_message(self, cleaned_data):
      return self.success_message % dict(
            cleaned_data,
            hospital_admin=self.object.hospital_admin.get_full_name,
        )


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = User.objects.filter(email=obj.hospital_admin.email).first()
        print("User1:", user)
        print("Object:", obj)

        form = HospitalProfileModelForm(request.POST or None, instance=obj)
        user_form = UserUpdateForm(request.POST or None, instance=user)
        
        if user_form.is_valid() and form.is_valid():
            hospital_profile = form.save(commit = False)
            if hospital_profile.application_status >2:
                pass
            else:
                hospital_profile.application_status = 2
            hospital_profile.save()
            

            user = user_form.save(commit=False)
            user.is_active = True  
            user.hospital = True
            user.save()
            hospital = Hospital.objects.filter(hospital_admin=user).first()        
            messages.success(request, 'Hospital Profile Update Successful')
            return redirect(hospital.get_absolute_url())
        else:
            messages.error(request, 'Hospital Profile Update Failed.')
            hospital = Hospital.objects.filter(hospital_admin=user).first() 
            return redirect(hospital.get_absolute_url())
        return super(UpdateHospitalProfileDetails, self).form_valid(form and user_form)






class MyApplicationListView00001(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_tables.html"
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user

        # Get all application numbers for the user
        application_nos = Document.objects.filter(
            hospital_name__hospital_admin=user
        ).values_list("application_no", flat=True).distinct()

        # Fetch all related data
        documents = Document.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Document", output_field=CharField()))

        payments = Payment.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Payment", output_field=CharField()))

        schedules = Schedule.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Schedule", output_field=CharField()))

        inspections = Inspection.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Inspection", output_field=CharField()))

        licenses = License.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("License", output_field=CharField()))

        internship = Appraisal.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Internship", output_field=CharField()))

        # Combine all querysets into a list
        combined_qs = list(chain(documents, payments, schedules, inspections, licenses, internship))

        # Create a priority order for model processing
        model_priority = {
            "Document": 6,
            "Payment": 5,
            "Schedule": 4,
            "Inspection": 3,
            "License": 2,
            "Internship": 1,
        }

        # Sort by application_no and priority of the model
        combined_qs.sort(
            key=lambda obj: (
                obj.application_no,
                model_priority[obj.model_name],
            )
        )

        # Group by application_no, keeping only the highest priority entry
        most_recent = {}
        for obj in combined_qs:
            if obj.application_no not in most_recent:
                most_recent[obj.application_no] = obj

        return list(most_recent.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = self.get_queryset()
        hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        context["hospitals"] = hospital
        context["applications"] = applications
        print("my applications list:", applications)
        print("my hospitals list:", hospital)

        # Safely add hospital_name to context
        if applications:
            context["hospital_name"] = applications[0].hospital_name
        else:
            context["hospital"] = hospital

        return context

class MyApplicationListView00000(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_tables.html"
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user

        # Get all application numbers for the user
        application_nos = Document.objects.filter(
            hospital_name__hospital_admin=user
        ).values_list("application_no", flat=True).distinct()

        # Fetch all related data
        documents = Document.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Document", output_field=CharField()))

        payments = Payment.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Payment", output_field=CharField()))

        schedules = Schedule.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Schedule", output_field=CharField()))

        inspections = Inspection.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Inspection", output_field=CharField()))

        internship = Appraisal.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("Internship", output_field=CharField()))

        licenses = License.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(model_name=Value("License", output_field=CharField()))

        # Combine all querysets into a list
        combined_qs = list(chain(documents, payments, schedules, inspections, internship, licenses))

        # Create a priority order for model processing
        model_priority = {
            "Document": 1,
            "Payment": 2,
            "Schedule": 3,
            "Inspection": 4,
            "Internship": 5,
            "License": 6,
        }

        # Sort by application_no and priority of the model
        combined_qs.sort(
            key=lambda obj: (
                obj.application_no,
                model_priority[obj.model_name],
            )
        )

        # Group by application_no, keeping only the highest priority entry
        most_recent = {}
        for obj in combined_qs:
            if obj.application_no not in most_recent:
                most_recent[obj.application_no] = obj

        return list(most_recent.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = self.get_queryset()
        context["applications"] = applications
        print("my applications list:", applications)


        # Safely add hospital_name to context
        if applications:
            context["hospital_name"] = applications[0].hospital_name
        else:
            context["hospital_name"] = None

        return context


class MyApplicationListView000(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_tables.html"
    context_object_name = 'applications'

    def get_queryset(self):
        # Filter data for the logged-in user
        user = self.request.user
        application_nos = Document.objects.filter(hospital_name__hospital_admin=user).values_list('application_no', flat=True).distinct()
        
        # Query all relevant models
        documents = Document.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('date', 'date'))
        

        payments = Payment.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('payment_date', 'payment_date'))

        schedules = Schedule.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('inspection_schedule_date', 'inspection_schedule_date'))

        inspections = Inspection.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('inspection_date', 'inspection_date'))

        licenses = License.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('issue_date', 'issue_date'))
        
        internship = Appraisal.objects.filter(
            hospital_name__hospital_admin=user, application_no__in=application_nos
        ).annotate(last_updated=Coalesce('appraisal_date', 'appraisal_date'))


        # Combine all querysets
        combined_qs = sorted(
            chain(documents, payments, schedules, inspections, licenses, internship),
            key=lambda x: x.last_updated,
            reverse=True
        )

        # Group by application_no and take the most recent entry for each
        most_recent = {}
        for obj in combined_qs:
            if obj.application_no not in most_recent:
                most_recent[obj.application_no] = obj

        return list(most_recent.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.get_queryset()
        applications = self.get_queryset()
        hospital_name = applications[0]
        context['hospital_name'] = hospital_name
        print("my applications list:", applications)
        return context




class MyApplicationListView0(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table.html"
    context_object_name = 'object'
    model = Document


    def get_hospital_query(self, license_type, application_type, application_status=None):
        qs = Hospital.objects.select_related("hospital_admin").filter(
        hospital_admin=self.request.user,
        type=license_type
        )
        if application_status:
            qs = qs.filter(application_status=application_status)
        return qs


    def generate_application_queries(self, model, license_types, application_types, application_statuses):
        context = {}
        for license_type in license_types:
            for application_type in application_types:
                for status in application_statuses:
                    context[f"{license_type}_{application_type}_{status}"] = model.objects.filter(
                    hospital_name__hospital_admin=self.request.user,
                    license_type=license_type,
                    application_type=application_type,
                    application_status=status)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hospital_types = [
            'Radiography Practice Permit',
            'Gov Internship Accreditation',
            'Pri Internship Accreditation',
            'Radiography Practice Permit Renewal',
            'Pri Internship Accreditation Renewal',
            'Gov Internship Accreditation Renewal'
            ]
    
        # Get hospital queries dynamically
        for hospital_type in hospital_types:
            context[f'hospital_qs_{hospital_type}'] = Hospital.objects.select_related("hospital_admin").filter(
            hospital_admin=self.request.user, type=hospital_type
            )
    
            # Get document, payment, schedule, etc. queries in a similar manner
        license_types = ['Radiography Practice Permit', 'Internship Accreditation']
        application_types = [
            'New Registration - Radiography Practice Permit', 
            'New Registration - Government Hospital Internship',
            'New Registration - Private Hospital Internship',
            'Renewal - Radiography Practice Permit',
            'Renewal - Private Hospital Internship',
            'Renewal - Government Hospital Internship'
            ]
    
        context.update(self.generate_application_queries(Document, license_types, application_types, application_statuses=[1, 2, 3, 4, 5, 6, 7, 8]))
    
            # You can do something similar for other models like Payment, Schedule, etc.
    
        return context


class MyApplicationListView99(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table.html"
    context_object_name = 'object'
    model = Document

    APPLICATION_STATUSES = [1, 2, 3, 4, 5, 6, 7, 8]  # Move statuses to a constant for reusability

    def get_hospital_query(self, license_type, application_status=None):
        qs = Hospital.objects.select_related("hospital_admin").filter(
            hospital_admin=self.request.user,
            type=license_type
        )
        if application_status:
            qs = qs.filter(application_status=application_status)
        return qs

    def generate_application_queries(self, model, license_types, application_types, application_statuses, application_no):
        context = {
            f"{license}_{app_type}_{status}": model.objects.filter(
                hospital_name__hospital_admin=self.request.user,
                license_type=license,
                application_type=app_type,
                application_status=status,
                application_no=application_no
            )
            for license in license_types
            for app_type in application_types
            for status in application_statuses
        }
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch all relevant hospital types in a single query to avoid redundancy
        hospital_types = [
            'Radiography Practice Permit',
            'Gov Internship Accreditation',
            'Pri Internship Accreditation',
            'Radiography Practice Permit Renewal',
            'Pri Internship Accreditation Renewal',
            'Gov Internship Accreditation Renewal'
        ]
        hospitals = Hospital.objects.select_related("hospital_admin").filter(
            hospital_admin=self.request.user, type__in=hospital_types
        )

        # Update context with hospitals categorized by type
        for hospital_type in hospital_types:
            context[f'hospital_qs_{hospital_type}'] = hospitals.filter(type=hospital_type)

        # Define license and application types for querying
        license_types = ['Radiography Practice Permit', 'Internship Accreditation']
        application_types = [
            'New Registration - Radiography Practice Permit', 
            'New Registration - Government Hospital Internship',
            'New Registration - Private Hospital Internship',
            'Renewal - Radiography Practice Permit',
            'Renewal - Private Hospital Internship',
            'Renewal - Government Hospital Internship'
        ]

        # Generate and update context with application queries
        context.update(
            self.generate_application_queries(
                Document, license_types, application_types, self.APPLICATION_STATUSES
            )
        )

        return context


class MyApplicationListView2(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table3.html"
    context_object_name = 'object'
    model = Document
         
    def get_context_data(self, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Radiography Practice')
        context['hospital_qss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Gov Internship Accreditation')
        context['hospital_qsss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Pri Internship Accreditation')
        q1 = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice', application_type = 'Renewal - Radiography Practice')
        q2 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q3 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q4 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q5 = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        context['li_stage'] =  chain(q5, q4, q3, q2, q1)
        context['reg_stage'] = chain(q4, q3)
        context['pvs_stage'] = chain(q3, q2)
        context['pym_stage'] = q2
        context['doc_stage'] = q1        
        return context

class MyApplicationListView00(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_tables.html"
    context_object_name = 'documents'
    model = Document

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     application_no = self.request.GET.get("application_no", None)  # Get 'application_no' from the query parameters
    #     if application_no:
    #         queryset = queryset.filter(application_no=application_no)
    #     return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        application_no = self.request.GET.get("application_no")
        if application_no:
            queryset = queryset.filter(
            hospital_name__hospital_admin=self.request.user,
            application_no=application_no
            )
        else:
            queryset = queryset.filter(hospital_name__hospital_admin=self.request.user)
        return queryset



    def get_context_data(self, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(**kwargs)
        user_application_nos = Document.objects.filter(hospital_name__hospital_admin=self.request.user).values_list('application_no', flat=True).distinct()
        document_qs = Document.objects.filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type='Radiography Practice Permit', application_type='New Registration - Radiography Practice Permit', application_no__in=user_application_nos).distinct('application_no')  # Ensure each application_no is unique if needed
        context['document_qs'] = document_qs
        user_applications = License.objects.filter(hospital_name__hospital_admin=self.request.user).values_list('application_no', flat=True).distinct()
        license_issue_qs = License.objects.filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit', application_no__in=user_application_nos).distinct('application_no')  # Ensure each application_no is unique if needed
        context['license_issue_qs'] = license_issue_qs
        application_nos = Document.objects.filter(hospital_name__hospital_admin=self.request.user).values_list('application_no', flat=True) 
        # user_documents = Document.objects.filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type='Radiography Practice Permit', application_type='New Registration - Radiography Practice Permit')
        # unique_documents = user_documents.order_by('application_no').distinct('application_no')
        # context['document_qs'] = unique_documents
        context['application_nos'] = application_nos
        # user_li_docs = License.objects.filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        # li_unique_docs = user_li_docs.order_by('application_no').distinct('application_no')
        # license_issue_qs = li_unique_docs
        print ("License N Set:", license_issue_qs)
        # context['license_issue_qs'] = li_unique_docs
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Radiography Practice Permit')
        context['hospital_qss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Gov Internship Accreditation')
        context['hospital_qsss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Pri Internship Accreditation')
        context['hospital_qsr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Radiography Practice Permit Renewal')
        context['hospital_qssr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Pri Internship Accreditation Renewal')
        context['hospital_qgssr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Gov Internship Accreditation Renewal')
        # context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user,  application_status=1, license_type='Radiography Practice Permit', application_type='New Registration - Radiography Practice Permit', application_no__in=application_nos )
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice Permit', application_type = 'New Registration - Radiography Practice Permit', **({'application_no': application_no} if application_no else {}))
        context['document_qss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Government Hospital Internship')
        context['document_qsss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Private Hospital Internship')
        context['document_qsr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice Permit', application_type = 'Renewal - Radiography Practice Permit')
        context['document_qssr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Private Hospital Internship')
        context['document_qgssr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Government Hospital Internship')
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['payment_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['payment_qgssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['payment_verified_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_verified_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_verified_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_verified_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['payment_verified_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['payment_verified_qgssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['schedule_qss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['schedule_qsss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['schedule_qssr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['schedule_qgssr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['inspection_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['inspection_approved_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['accreditation_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['accreditation_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['accreditation_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['accreditation_approved_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_approved_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['accreditation_approved_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['accreditation_approved_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['registrar_approval_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['registrar_approval_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['registrar_approval_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['registrar_approval_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['registrar_approval_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['registrar_approval_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['license_issue_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['license_issue_qss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['license_issue_qsss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['license_issue_qsr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['license_issue_qssr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['license_issue_qgssr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        #context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        #context['inspection_approved_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        #context['registrar_approval_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        # license_issue_qs = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit', application_no__in=application_nos )
        # print ("License Set:", license_issue_qs)
        # document_qs = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user,  application_status=1, license_type='Radiography Practice Permit', application_type='New Registration - Radiography Practice Permit', application_no__in=application_nos )
        # print ("Document Set:", document_qs)
        return context 


class HospitalObjectMixin(object):
    model = Hospital
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class ChangeApplicationType(LoginRequiredMixin, ListView, UpdateView):
    template_name = "hospitals/change_application_category.html"
    context_object_name = 'object_list'  # Ensures queryset is properly named
    form_class = HospitalProfileUpdateModelForm  # Use form_class for UpdateView
    model = Hospital  # Required for UpdateView

    def get_queryset(self):
        """Filter hospitals by the logged-in user."""
        return Hospital.objects.filter(hospital_admin=self.request.user)

    def get_object(self, queryset=None):
        """Return a single hospital instance for UpdateView."""
        return self.get_queryset().first()  # Get the first hospital for the logged-in admin

    def get_context_data(self, **kwargs):
        """Ensure object_list and form are properly included in the context."""
        # Manually set self.object before calling super()
        self.object = self.get_object()  
        # Now call super() with self.object set
        context = super().get_context_data(**kwargs)
        # Explicitly set object_list for ListView functionality
        context['object_list'] = self.get_queryset()
        context['hospital_name'] = self.get_queryset()
        # Ensure hospital object is available for UpdateView
        context['object'] = self.object
        # Preserve form state in case of validation errors
        context['form'] = kwargs.get('form', self.form_class(instance=self.object))
        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital application type updated successfully!")
            return redirect(reverse("hospitals:application_list"))  # Redirect after success
        else:
            # Ensure object_list and object are passed explicitly during re-render
            return self.render_to_response(self.get_context_data(form=form))



class StartNewApplication(LoginRequiredMixin, HospitalObjectMixin, ListView):
    template_name = "hospitals/start_new_application.html"
    context_object_name = 'object'

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Hospital.objects.filter(hospital_admin=self.request.user)

    def get_context_data(self, **kwargs):
        obj = super(StartNewApplication, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        
        return obj  

class StartNewPriInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})
    def get_initial(self):   
        return {
            'hospital_name': self.kwargs["pk"],        
        }
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user) 
    def get_context_data(self, **kwargs):
        context = super(StartNewPriInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class StartNewGovInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})
    def get_initial(self):   
        return {
            'hospital_name': self.kwargs["pk"],        
        }
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user) 
    def get_context_data(self, **kwargs):
        context = super(StartNewGovInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class StartGovInternshipApplication(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/start_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):  
        """Set initial data for the form, ensuring 'pk' exists in kwargs"""
        initial = super().get_initial()
        if "pk" in self.kwargs:
            initial["hospital_name"] = self.kwargs["pk"]
        return initial

    def get_queryset(self):
        """Filter documents by hospitals managed by the logged-in user."""
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)

    def get_context_data(self, **kwargs):
        """Add hospital queryset to the context for form selection."""
        context = super().get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)


    # def form_valid(self, form):
    #     self.object = form.save(commit=False)

    #     errors = []

    #     # Validate and assign Radiographers (Max 3)
    #     for i in range(1, 4):
    #         radiographer_key = f'radiographer{i}'
    #         license_no_key = f'radiographer{i}_license_no'
    #         radiographer = self.request.POST.get(radiographer_key)
    #         license_no = self.request.POST.get(license_no_key)

    #         if radiographer and license_no:
    #             setattr(self.object, radiographer_key, radiographer)
    #             setattr(self.object, license_no_key, license_no)
    #         elif i == 1:
    #             errors.append("Radiographer 1 details are required.")

    #     # Validate and assign Radiographer Licenses (Max 3)
    #     for i in range(1, 4):
    #         radiographer_license_key = f'radiographer{i}_practice_license'  # ✅ Correct field name
    #         radiographer_license = self.request.FILES.get(radiographer_license_key)  # ✅ Retrieve from FILES

    #         if radiographer_license:
    #             setattr(self.object, radiographer_license_key, radiographer_license)
    #         elif i == 1:  # Ensure at least the first one is required
    #             errors.append("Radiographer 1 Practice License is required.")


    #     # Validate and assign Other Staff (Max 6)
    #     for i in range(1, 6):
    #         staffname_key = f'staffname{i}'
    #         staffdesignation_key = f'staffdesignation{i}'  # Fixed Key
    #         staffname = self.request.POST.get(staffname_key)
    #         staffdesignation = self.request.POST.get(staffdesignation_key)

    #         if staffname and staffdesignation:
    #             setattr(self.object, staffname_key, staffname)
    #             setattr(self.object, staffdesignation_key, staffdesignation)
    #         elif i == 1:
    #             errors.append("Staff 1 details are required.")

    #     # If any errors exist, return form invalid with messages
    #     if errors:
    #         for error in errors:
    #             messages.error(self.request, error)
    #         return self.form_invalid(form)

    #     self.object.save()
    #     return super().form_valid(form)

    def form_invalid(self, form):
        """Ensure form errors are properly handled."""
        return self.render_to_response(self.get_context_data(form=form))

class StartPriInternshipApplication(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/start_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):  
        """Set initial data for the form, ensuring 'pk' exists in kwargs"""
        initial = super().get_initial()
        if "pk" in self.kwargs:
            initial["hospital_name"] = self.kwargs["pk"]
        return initial

    def get_queryset(self):
        """Filter documents by hospitals managed by the logged-in user."""
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)

    def get_context_data(self, **kwargs):
        """Add hospital queryset to the context for form selection."""
        context = super().get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)

    #     errors = []

    #     # Validate and assign Radiographers (Max 3)
    #     for i in range(1, 4):
    #         radiographer_key = f'radiographer{i}'
    #         license_no_key = f'radiographer{i}_license_no'
    #         radiographer = self.request.POST.get(radiographer_key)
    #         license_no = self.request.POST.get(license_no_key)

    #         if radiographer and license_no:
    #             setattr(self.object, radiographer_key, radiographer)
    #             setattr(self.object, license_no_key, license_no)
    #         elif i == 1:
    #             errors.append("Radiographer 1 details are required.")

    #     # Validate and assign Radiographer Licenses (Max 3)
    #     for i in range(1, 4):
    #         radiographer_license_key = f'radiographer{i}_practice_license'  # ✅ Correct field name
    #         radiographer_license = self.request.FILES.get(radiographer_license_key)  # ✅ Retrieve from FILES

    #         if radiographer_license:
    #             setattr(self.object, radiographer_license_key, radiographer_license)
    #         elif i == 1:  # Ensure at least the first one is required
    #             errors.append("Radiographer 1 Practice License is required.")



    #     # Validate and assign Other Staff (Max 6)
    #     for i in range(1, 6):
    #         staffname_key = f'staffname{i}'
    #         staffdesignation_key = f'staffdesignation{i}'  # Fixed Key
    #         staffname = self.request.POST.get(staffname_key)
    #         staffdesignation = self.request.POST.get(staffdesignation_key)

    #         if staffname and staffdesignation:
    #             setattr(self.object, staffname_key, staffname)
    #             setattr(self.object, staffdesignation_key, staffdesignation)
    #         elif i == 1:
    #             errors.append("Staff 1 details are required.")

    #     # If any errors exist, return form invalid with messages
    #     if errors:
    #         for error in errors:
    #             messages.error(self.request, error)
    #         return self.form_invalid(form)

    #     self.object.save()
    #     return super().form_valid(form)

    def form_invalid(self, form):
        """Ensure form errors are properly handled."""
        return self.render_to_response(self.get_context_data(form=form))


class StartNewRadApplication(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/register_radiography_practice.html'
    form_class = HospitalDetailModelForm
    
    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})
    
    def get_initial(self):
        return {
            'hospital_name': self.kwargs["pk"],   
        }
    
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add hospital queryset to the context for form selection."""
        context = super().get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Ensure form errors are properly handled."""
        return self.render_to_response(self.get_context_data(form=form))



class UpdateRadApplication(LoginRequiredMixin, UpdateView):
    model = Document
    template_name = 'hospitals/update_radiography_practice.html'
    form_class = HospitalUpdateModelForm
    pk_url_kwarg = 'pk'  # Match URL kwarg used in reverse() and get_success_url

    def get_queryset(self):
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Application successfully updated.")
        return reverse("hospitals:application_update_details", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        context["is_update"] = True  # You can use this in your template to toggle buttons/titles
        return context


    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Handle Radiographers (max 3)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            setattr(self.object, radiographer_key, radiographer or '')
            setattr(self.object, license_no_key, license_no or '')
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Handle Other Staff (max 6)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            setattr(self.object, staffname_key, staffname or '')
            setattr(self.object, staffdesignation_key, staffdesignation or '')

        self.object.save()
        Payment.objects.filter(hospital=self.object).update(vet_status=1)

        return super().form_valid(form)

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)

    #     # Handle Radiographers (max 3)
    #     for i in range(1, 4):
    #         radiographer_key = f'radiographer{i}'
    #         license_no_key = f'radiographer{i}_license_no'
    #         license_file_key = f'radiographer{i}_practice_license'

    #         radiographer = self.request.POST.get(radiographer_key)
    #         license_no = self.request.POST.get(license_no_key)
    #         license_file = self.request.FILES.get(license_file_key)

    #         setattr(self.object, radiographer_key, radiographer or '')
    #         setattr(self.object, license_no_key, license_no or '')

    #         if license_file:
    #             setattr(self.object, license_file_key, license_file)

    #     # Handle Other Staff (max 6)
    #     for i in range(1, 7):
    #         staffname_key = f'staffname{i}'
    #         staffdesignation_key = f'staffdesignation{i}'

    #         staffname = self.request.POST.get(staffname_key)
    #         staffdesignation = self.request.POST.get(staffdesignation_key)

    #         setattr(self.object, staffname_key, staffname or '')
    #         setattr(self.object, staffdesignation_key, staffdesignation or '')

    #     self.object.save()
    #     return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class StartNewPracticePermitRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_radiography_hospital_license.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:start_radiography_license_renewal_details", kwargs={"id": self.object.id})
    def get_initial(self):
        return {
            'hospital_name': self.kwargs["pk"],
        }
    
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)    
    def get_context_data(self, **kwargs):
        context = super(StartNewPracticePermitRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class StartPriInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})
    #def get_initial(self):   
        #return {
            #'hospital': self.kwargs["pk"],        
        #}
    def get_form_kwargs(self):
        self.license = License.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user) 
    def get_context_data(self, **kwargs):
        context = super(StartPriInternshipRenewal, self).get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class StartGovInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})
    #def get_initial(self):    
        #return {
            #'hospital': self.kwargs["pk"],       
        #}
    def get_form_kwargs(self):
        self.license = License.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)   
    def get_context_data(self, **kwargs):
        context = super(StartGovInternshipRenewal, self).get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UpdateIntApplication(LoginRequiredMixin, UpdateView):
    model = Document
    template_name = 'hospitals/update_internship_accreditation.html'
    form_class = HospitalUpdateModelForm
    pk_url_kwarg = 'pk'  # Match URL kwarg used in reverse() and get_success_url

    def get_queryset(self):
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Application successfully updated.")
        return reverse("hospitals:application_update_details", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        context["is_update"] = True  # You can use this in your template to toggle buttons/titles
        return context


    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Handle Radiographers (max 3)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            setattr(self.object, radiographer_key, radiographer or '')
            setattr(self.object, license_no_key, license_no or '')
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Handle Other Staff (max 6)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            setattr(self.object, staffname_key, staffname or '')
            setattr(self.object, staffdesignation_key, staffdesignation or '')

        self.object.save()
        Payment.objects.filter(hospital=self.object).update(vet_status=1)

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))



class StartRadiographyLicenseRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_radiography_hospital_license.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:start_radiography_license_renewal_details", kwargs={"id": self.object.id})
    #def get_initial(self):
        #return {
            #'hospital': self.kwargs["pk"],
        #}
    def get_form_kwargs(self):
        self.license = License.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)    
    def get_context_data(self, **kwargs):
        context = super(StartRadiographyLicenseRenewal, self).get_context_data(**kwargs)
        context["hospital_qs"] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context
    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Assign Radiographers (Max 3, all optional)
        for i in range(1, 4):
            radiographer_key = f'radiographer{i}'
            license_no_key = f'radiographer{i}_license_no'
            license_file_key = f'radiographer{i}_practice_license'

            radiographer = self.request.POST.get(radiographer_key)
            license_no = self.request.POST.get(license_no_key)
            license_file = self.request.FILES.get(license_file_key)

            if radiographer and license_no:
                setattr(self.object, radiographer_key, radiographer)
                setattr(self.object, license_no_key, license_no)
            # Even if the names/numbers aren't set, allow uploading the license file
            if license_file:
                setattr(self.object, license_file_key, license_file)

        # Assign Other Staff (Max 6, all optional)
        for i in range(1, 7):
            staffname_key = f'staffname{i}'
            staffdesignation_key = f'staffdesignation{i}'

            staffname = self.request.POST.get(staffname_key)
            staffdesignation = self.request.POST.get(staffdesignation_key)

            if staffname and staffdesignation:
                setattr(self.object, staffname_key, staffname)
                setattr(self.object, staffdesignation_key, staffdesignation)

        self.object.save()
        return super().form_valid(form)

    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class StartApplication(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/hospitals_register.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})
    def get_initial(self):
        return {
            'hospital_name': self.kwargs["pk"],    
        }
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
    def get_context_data(self, **kwargs):
        context = super(StartApplication, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def get_form_kwargs(self):
        self.hospital = Hospital.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        #kwargs['initial']['license_type'] = self.hospital.license_type
        return kwargs
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class RegistrationObjectMixin(object):
    model = Document
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class HospitalDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/hospitals_reg_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)



class ApplicationUpdateDetails(LoginRequiredMixin, DetailView):
    template_name = "hospitals/application_update_details.html"
    model = Document




class PrivateHospitalDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/private_hospital_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]
            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)
            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)


class StartRadiographyLicenseRenewalDetails(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/start_hospital_radiography_license_renewal_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)


class FacilityDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/hospitals_reg_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message2.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)



#class FacilityDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    #template_name = 'hospitals/facility_reg_confirmation.html' 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = BasicDetailModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form


            #subject = 'Acknowledgment of Interest to Obtain Internship Accreditation'
            #from_email = settings.DEFAULT_FROM_EMAIL
            #to_email = [request.user.email]

            #context['form'] = form
            #contact_message = get_template(
               #'hospitals/contact_message2.txt').render(context)

            #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)

        #return render(request, self.template_name, context)



class GenerateInvoiceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_rad_permit_invoice.html"
    model = Document
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class GenerateRenewalInvoice(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_renewal_invoice.html"
    model = Document
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class GenerateAccreditationInvoice(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_accreditation_invoice.html"
    model = Document

    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
    
    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }

    def get_context_data(self, **kwargs):
        obj = super(GenerateAccreditationInvoice, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #obj['license_history_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        return obj  


class GenerateAccreditationPaymentDetails(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_gov_accreditation_invoice.html"
    model = Document

    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
    
    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }

    def get_context_data(self, **kwargs):
        obj = super(GenerateAccreditationPaymentDetails, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #obj['license_history_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        return obj 

class PayAccreditationFee1(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/pay_accreditation_fee.html'
    form_class = PaymentDetailsModelForm

    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        """Provide additional context for the template."""
        context = super().get_context_data(**kwargs)
        
        # Retrieve the document instance related to the form
        document = self.get_document()

        # Add related querysets to the context
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=document.hospital_name)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        
        return context

    def get_initial(self):
        """Provide initial values for the form fields."""
        document = self.get_document()
        return {
            'hospital': document.hospital_name.id,
        }

    def get_form_kwargs(self):
        """Add additional data to the form."""
        kwargs = super().get_form_kwargs()
        document = self.get_document()

        kwargs['initial'] = {
            'hospital_name': document.hospital_name,
            'application_no': document.application_no,
        }
        return kwargs

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        messages.error(self.request, "There was an error with your submission. Please check the form.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_document(self):
        """Retrieve and cache the document object."""
        if not hasattr(self, '_document'):
            self._document = get_object_or_404(Document, pk=self.kwargs['pk'])
        return self._document


class PayAccreditationFee0(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/pay_accreditation_fee.html'
    form_class = PaymentDetailsModelForm
    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=self.document.hospital_name)
        #context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice')
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context
    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        } 
    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no   
        return kwargs
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())



class PayAccreditationFee(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/pay_accreditation_fee.html'
    form_class = PaymentDetailsModelForm

    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Safely get the Document object
        self.document = get_object_or_404(Document, pk=self.kwargs['pk'])
        # Query relevant hospital details
        context['document_qs'] = Document.objects.filter(hospital_name=self.document.hospital_name)
        context['hospital_qs'] = Hospital.objects.filter(hospital_admin=self.request.user)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        } 

    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no   
        return kwargs

    def form_invalid(self, form):
        """Handle invalid form submission gracefully."""
        return self.render_to_response(self.get_context_data(form=form))


class PaymentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/payment_processing.html'
    form_class = PaymentDetailsModelForm
    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=self.document.hospital_name)
        #context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice')
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context
    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        } 
    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no   
        return kwargs
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())



 
class StartLicenseRenewal(LoginRequiredMixin, DetailView):
    template_name = "hospitals/start_renewal.html"
    model = License
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class RenewalPaymentCreateView(LoginRequiredMixin, RegistrationObjectMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/renewal_payment_processing.html'
    form_class = PaymentDetailsModelForm

    def get_success_url(self):
        return reverse("hospitals:renewal_payment_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        #context['document_qsr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Radiography Practice', application_type = 'Renewal')
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
         

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class PaymentDetailView(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = 'hospitals/payment_details_submission.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Receipt of Registration Fee Payment Details'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)

class RenewalPaymentDetailView(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = 'hospitals/renewal_payment_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Receipt of Registration Fee Payment Details'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)

class PaymentVerificationObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class PaymentVerificationsView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/payment_verification_details.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AccreditationPaymentVerifications(LoginRequiredMixin, DetailView):
    template_name = "hospitals/accreditation_payment_verification_details.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class VerificationsCompleted(LoginRequiredMixin, DetailView):
    template_name = "hospitals/verifications_done.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.object.hospital
        context['application'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class AccreditationVerificationsCompleted(LoginRequiredMixin, DetailView):
    template_name = "hospitals/verifications_done.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.object.hospital
        context['application'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class ScheduleDetailView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_schedule_details.html"
    model = Schedule
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class InspectionView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_report_detail.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AppraisalView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/appraisal_report_detail.html"
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AccreditationInspectionApprovedView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/accreditation_report_approved.html"
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context



class InspectionApprovedView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_report_approved.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AppraisalObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionListView(View):
    template_name = "hospitals/inspection_report_table.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_status=2)
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class LicenseIssuanceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/license_issuance.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class PracticePermitRenewalFinalApproval(LoginRequiredMixin, DetailView):
    template_name = "hospitals/practice_permit_renewal_final_approval.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class InternshipLicenseIssuanceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/internship_license_issuance.html" 
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context 

#class InternshipLicenseIssuanceView(LoginRequiredMixin, AppraisalObjectMixin, View):
    #template_name = "hospitals/internship_license_issuance.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)            

#class InspectionView(LoginRequiredMixin, InspectionObjectMixin, View):
    #template_name = "hospitals/inspection_report_detail.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)

#class VerificationsSuccessfulView(LoginRequiredMixin, PaymentVerificationObjectMixin, View):
    #template_name = "hospitals/verifications_successful.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #context = {'hospital_qs': Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)}
        #return render(request, self.template_name, context)

#class ScheduleDetailView(LoginRequiredMixin, ScheduleObjectMixin, View):
    #template_name = "hospitals/inspection_schedule_details.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)


class LicenseObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj   


class MyLicensesDetailView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/license_application_summary.html"
    model = License
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context



class MyLicenseApplicationsHistory(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_license_history.html"
    context_object_name = 'object'

    def get_queryset(self):
        return License.objects.filter(hospital_name__hospital_admin=self.request.user)
    def get_context_data(self, **kwargs):
        obj = super(MyLicenseApplicationsHistory, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        obj['permit_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit')
        #obj['permit_qs'] = License.objects.all()
        obj['certificate_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation')
        return obj  



class MyLicenseApplicationsHistory(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_license_history.html"
    context_object_name = 'object'

    def get_queryset(self):
        # Get all licenses related to hospitals administered by the current user
        return License.objects.filter(hospital_name__hospital_admin=self.request.user)


    def get_context_data(self, **kwargs):
        obj = super(MyLicenseApplicationsHistory, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(
            hospital_admin=self.request.user
        )
        permit_qs = License.objects.select_related("hospital_name").filter(
            hospital_name__hospital_admin=self.request.user,
            hospital__license_type='Radiography Practice Permit'
        )
        certificate_qs = License.objects.select_related("hospital_name").filter(
            hospital_name__hospital_admin=self.request.user,
            hospital__license_type='Internship Accreditation'
        )

        combined_qs = list(chain(permit_qs, certificate_qs))

        obj['combined_qs'] = combined_qs
        return obj

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user

    #     # Fetch hospital and license querysets
    #     hospital_qs = Hospital.objects.filter(hospital_admin=user)
    
    #     permit_qs = License.objects.filter(
    #         hospital_name__hospital_admin=user,
    #         hospital_name__license_type='Radiography Practice Permit'
    #     )
    #     certificate_qs = License.objects.filter(
    #         hospital_name__hospital_admin=user,
    #         hospital_name__license_type='Internship Accreditation'
    #     )

    #     # Combine permit_qs and certificate_qs
    #     combined_qs = list(chain(permit_qs, certificate_qs))

    #     # Add data to the context
    #     context['hospital_qs'] = hospital_qs
    #     context['combined_qs'] = combined_qs  # Combined permits and certificates
    #     return context


#class StartLicenseRenewal(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = "hospitals/start_renewal.html" # DetailView
    #def get(self, request, id=None, *args, **kwargs):
        # GET method
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context) 




#class StartApplication(LoginRequiredMixin, CreateView):
    #template_name = 'hospitals/hospitals_register.html'

    #form_class = HospitalDetailModelForm

    #def get_success_url(self):
        #return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})



class HospitalRenewView(CreateView):
    template_name = 'hospitals/hospitals_register.html'

    form_class = HospitalDetailModelForm
  


def reg_table(request):
     return render(request, 'hospitals/reg_table.html')


class RegisterFacility(LoginRequiredMixin, CreateView):
    template_name = 'hospitals/hospitals_register.html'

    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:facility_details", kwargs={"id": self.object.id})


class PaymentProcessing(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "hospitals/payment_processing.html"
    template_name1 = 'hospitals/payment_details_submitted.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        form = PaymentDetailsModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Receipt of Accreditation Fee Payment Details'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [request.user.email]

           context['form'] = form
           contact_message = get_template(
               'hospitals/payment_message2.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)  
        
        return render(request, self.template_name1, context)




class PaymentConfirmation(LoginRequiredMixin, PaymentVerificationObjectMixin, View):
    template_name = "hospitals/payment_verification_detail.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class PaymentVerificationListView(LoginRequiredMixin, View):
    template_name = "hospitals/payment_verification_table.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class ScheduleListView(LoginRequiredMixin, View):
    template_name = "hospitals/inspection_schedule_table.html"
    queryset = Schedule.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_zone="Enugu")
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class ScheduleObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class MyLicensesListView(LoginRequiredMixin, View):
    template_name = "hospitals/my_license_table.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)



def link_callback(uri, rel):
    sUrl = settings.STATIC_URL     
    sRoot = settings.STATIC_ROOT    
    mUrl = settings.MEDIA_URL       
    mRoot = settings.MEDIA_ROOT     
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path





class DownloadLicense(LoginRequiredMixin, LicenseObjectMixin, View):
    
    def get(self, request, *args, **kwargs):
        template = get_template('pdf/license.html')
        context = {
            'object': self.get_object()
        }
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf') 
        return None


#class StartLicenseRenewal(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = "hospitals/start_renewal.html" # DetailView
    #def get(self, request, id=None, *args, **kwargs):
        # GET method
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context) 


def download_rad_cert_reg(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(A4))
    object = get_object_or_404(License, pk=id)

    image_path1 = '%s/img/cert_border1.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=595, height=840)
    p.drawImage(image_path2, 250, 690, width=90, height=90)
  # Header Text
    p.setFont("Helvetica-Bold", 16, leading=None)
    p.drawCentredString(300, 660, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')

  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(300, 645, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')
    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(300, 580, 'Certificate of Registration of Practice')
    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(300, 560, 'This is to certify that')
    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(300, 500, str(object.hospital_name))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 480, str(object.hospital.facility_address))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 420, 'having satisfied all laid down conditions of the')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 400, 'Radiographers Registration Board of Nigeria')
    p.setFont("Helvetica", 16, leading=None)
    p.drawString(200, 330, 'have today')
    p.setFont("Helvetica", 16, leading=None)
    p.drawString(290, 330, str(object.issue_date))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 250, 'been registered as a practicing centre for')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 230, str(object.hospital.equipment))
    p.setFont("Helvetica", 14, leading=None)
    p.drawString(330, 130, 'Registrar/Secretary')
    p.drawImage(image_path3, 55, 90, width=120, height=120)
    p.drawImage(image_path4, 340, 145, width=110, height=60)
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 70, 'This Certificate shall remain the propery of Radiographers Registration Board of Nigeria (RRBN)')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 60, 'and shall, on demand, be surrendered to the Board')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 40, 'E-mail: info@rrbn.gov.ng')
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='certificate_of_registration_of_practice.pdf')


 


def download_rad_practice_permit(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(A4))
    object = get_object_or_404(License, pk=id)
    image_path1 = '%s/img/cert_border6.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    #image_path5 = '%s/img/passport.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=595, height=840)
    p.drawImage(image_path2, 150, 550, width=115, height=115)
  # Header Text
    p.setFont("Helvetica-Bold", 16, leading=None)
    p.drawCentredString(300, 780, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')
  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(300, 765, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')
    p.setFont("Helvetica", 10, leading=None)
    p.drawCentredString(455, 735, 'PERMIT NO: '+ str(object.license_no))
    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(150, 700, 'Year')
    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(200, 700, str(object.issue_date.strftime("%Y")))
    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(360, 700, 'Registration of Practice Permit')
    p.roundRect(355, 555, 110, 115, 4, stroke=1, fill=0)
    p.drawImage((object.hospital.radiographer_in_charge_passport.path), 356, 556, width=108, height=114)
    p.setFont("Helvetica", 7, leading=None)
    p.drawCentredString(410, 545, 'R.I.C RRBN LICENSE NO: '+ str(object.hospital.radiographer_in_charge_license_no))
    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(300, 485, 'This Permit is Issued to')
    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(300, 425, str(object.hospital_name))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 370, 'Located at ' + str(object.hospital.facility_address))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 305, 'In partial fullfillment of the conditions as a')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 280, 'Radiography Practicing Hospital/Centre')
    p.setFont("Helvetica", 14, leading=None)
    p.drawString(250, 130, 'Registrar/Secretary')
    p.setFont("Helvetica", 16, leading=None)
    p.drawString(390, 170, str(object.issue_date))
    p.setFont("Helvetica", 14, leading=None)
    p.drawString(410, 130, 'Date')
    p.drawImage(image_path3, 95, 110, width=120, height=120)
    p.drawImage(image_path4, 260, 145, width=110, height=60)
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 70, 'This permit shall remain the propery of Radiographers Registration Board of Nigeria (RRBN)')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 60, 'and shall, on demand, be surrendered to the Board')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 40, 'E-mail: info@rrbn.gov.ng')
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='registration_of_practice_permit.pdf')   



def download_accreditation_cert(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    object = get_object_or_404(License, pk=id)
    image_path1 = '%s/img/cert_border5.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=842, height=595)
    p.drawImage(image_path2, 380, 478, width=90, height=90)
  # Header Text
    p.setFont("Helvetica-Bold", 22, leading=None)
    p.drawCentredString(421, 450, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')
  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(421, 435, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')
    p.setFont("Helvetica", 9, leading=None)
    p.drawCentredString(670, 415, 'Certificate No: '+ str(object.license_no))
    p.setFont("Helvetica-Bold", 22, leading=None)
    p.drawCentredString(421, 380, 'Accreditation Certificate')
    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(421, 350, 'This is to certify that')
    p.setFont("Helvetica", 21, leading=None)
    p.drawCentredString(421, 315, str(object.hospital_name))
    p.setFont("Helvetica", 13, leading=None)
    p.drawCentredString(421, 295, str(object.hospital.facility_address))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 258, 'having satisfied all laid down conditions by Radiographers Registration Board of Nigeria')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 240, 'for accreditation of hospital/centre for training of Intern Radiographers')
    p.setFont("Helvetica", 16, leading=None)
    p.drawString(330, 200, 'have this day')
    p.setFont("Helvetica", 16, leading=None)
    p.drawString(435, 200, str(object.issue_date))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 160, 'been granted')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(455, 160, str(object.license_class))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 140, 'for the period')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(400, 140, str(object.issue_date))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(455, 140, 'to')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(511, 140, str(object.expiry_date))
    p.setFont("Helvetica", 14, leading=None)
    p.drawString(130, 100, 'Registrar/Secretary')
    p.drawImage(image_path3, 605, 65, width=120, height=120)
    p.drawImage(image_path4, 130, 110, width=110, height=60)
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(425, 45, 'This Certificate shall remain the propery of Radiographers Registration Board of Nigeria (RRBN) and shall, on demand, be surrendered to the Board')
    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(425, 30, 'E-mail: info@rrbn.gov.ng')
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='accreditation_certificate.pdf')   



@login_required
def lookup(request):
   registration = Registration.objects.all()

   context = {
     'registration': registration
   }
   return render(request, 'hospitals/hospitals_lookup.html', context)



