from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages, admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from wsgiref.util import FileWrapper
from accounts.models import Hospital
from accounts.decorators import monitoring_required
from hospitals.models import Payment, Document, Schedule, Inspection, License, Records, Appraisal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.views import View
from . import views
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)
from .forms import *
from .models import *
from accounts.forms import *
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib import messages
from xhtml2pdf import pisa
import os
import mimetypes
from django.contrib.staticfiles import finders
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from itertools import chain
from django.db.models import Max, Value, IntegerField, CharField, Q, Count
from operator import attrgetter
from django.db import models
from django.contrib.messages.views import SuccessMessageMixin
import itertools
counter = itertools.count()
import time
from django.http import JsonResponse
from itertools import chain
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import landscape, portrait
import io, csv
from django.contrib.auth.hashers import make_password
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.contrib.messages.views import SuccessMessageMixin
from datetime import date
from django.core.paginator import Paginator
from django.utils.timezone import now
from PIL import Image
from PIL import UnidentifiedImageError

User = get_user_model()


class StaffRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role == 'Monitoring':
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(StaffRequiredMixin, self).dispatch(request,
            *args, **kwargs)


class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)



@login_required
def monitoring_dashboard(request):
    current_year = now().year  # Get the current year

    # Count issued licenses where application_status=8
    license_count = License.objects.select_related("hospital_name").filter(issue_date__year=current_year, application_status=8).count()

    # Get all document applications for the current year
    document_applications = Document.objects.filter(date__year=current_year)

    due_for_payment = Document.objects.filter(application_status=1).count()

    current_payments = Payment.objects.filter(payment_date__year=current_year).count()

    # Get application numbers of issued licenses
    license_application_numbers = License.objects.values_list("application_no", flat=True)

    # Count pending license applications (Documents not in License)
    pending_license_applications = document_applications.exclude(application_no__in=license_application_numbers).count()

    # Count payments pending verification (vet_status = 1)
    pending_verifications = Payment.objects.filter(vet_status=1).count()
    completed_verifications = Payment.objects.filter(vet_status=2).exclude(hospital__application_type = 'Renewal - Radiography Practice Permit').count()

    schedules = Schedule.objects.select_related("hospital").all()
    inspections = Inspection.objects.select_related("hospital").all()
    appraisals = Appraisal.objects.select_related("hospital").all()

    # Convert QuerySets to dictionaries for fast lookup
    inspection_map = {insp.schedule_id: insp for insp in inspections}
    appraisal_map = {appr.schedule_id: appr for appr in appraisals}

    final_records = []  # Prevents duplicates

    # Process schedules and merge related inspections and appraisals
    pending_schedules_count = 0

    for schedule in schedules:
        schedule.is_inspection = schedule.id in inspection_map
        schedule.is_appraisal = schedule.id in appraisal_map
        schedule.is_pending = not (schedule.is_inspection or schedule.is_appraisal)

        if schedule.is_pending:
            pending_schedules_count += 1


    # Attach related inspection and appraisal details to schedule object
    schedule.inspection_date = inspection_map[schedule.id].inspection_date if schedule.is_inspection else None
    schedule.appraisal_date = appraisal_map[schedule.id].appraisal_date if schedule.is_appraisal else None

    final_records.append(schedule)

    # Sort with pending schedules first
    combined_records = sorted(final_records, key=lambda obj: obj.is_pending, reverse=True)

    # schedules = Schedule.objects.all()
    # inspections = Inspection.objects.select_related("hospital").all()
    # appraisals = Appraisal.objects.select_related("hospital").all()


    # Fetch schedules, inspections, and appraisals for the current year
    current_schedules = Schedule.objects.filter(inspection_schedule_date__year=current_year).select_related("hospital")
    current_inspections = Inspection.objects.filter(inspection_date__year=current_year).select_related("hospital")
    current_appraisals = Appraisal.objects.filter(appraisal_date__year=current_year).select_related("hospital")

    reg_approval_int = Appraisal.objects.filter(appraisal_status=2)
    reg_approval_rpp = Inspection.objects.filter(inspection_status=2)
    reg_approval_rppr = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')

    reg_approval_int_count = reg_approval_int.count()
    reg_approval_rpp_count = reg_approval_rpp.count()
    reg_approval_rppr_count = reg_approval_rppr.count()

    # Count inspections and appraisals separately
    schedules_count = schedules.count()
    current_schedules_count = current_schedules.count()
    current_inspections_count = current_inspections.count()
    current_appraisals_count = current_appraisals.count()

    # Calculate total count of inspections and appraisals
    total_inspections_appraisals = current_inspections_count + current_appraisals_count
    awaiting_reg_approval = reg_approval_int_count + reg_approval_rpp_count + reg_approval_rppr_count

    # Convert QuerySets to dictionaries for fast lookup
    # inspection_ids = set(inspections.values_list("schedule_id", flat=True))
    # appraisal_ids = set(appraisals.values_list("schedule_id", flat=True))


     # Track pending schedules count
    # pending_schedules_count = 0

    # Add flags to schedules
    # for schedule in schedules:
    #     schedule.is_inspection = schedule.id in inspection_ids
    #     schedule.is_appraisal = schedule.id in appraisal_ids
    #     schedule.is_pending = not (schedule.is_inspection or schedule.is_appraisal)

    #     if schedule.is_pending:
    #         pending_schedules_count += 1

    # Set flags for inspections & appraisals
    # for inspection in inspections:
    #     inspection.is_inspection = True
    #     inspection.is_pending = False

    # for appraisal in appraisals:
    #     appraisal.is_appraisal = True
    #     appraisal.is_pending = False

    # Combine all records and sort with pending schedules first
    # combined_records = sorted(
    #     chain(schedules, inspections, appraisals),
    #     key=lambda obj: obj.is_pending, 
    #     reverse=True  # Sorts `is_pending=True` first
    # )

    # Pass counts to template
    context = {
        'license_count': license_count,
        'due_for_payment': due_for_payment,
        'pending_verifications': pending_verifications,
        'pending_license_applications': pending_license_applications,
        'current_year': current_year,
        'current_payments': current_payments,
        'pending_schedules_count': pending_schedules_count,  # New count added
        'combined_records': combined_records,
        'completed_verifications': completed_verifications,
        'total_inspections_appraisals': total_inspections_appraisals,  # Total count added
        'awaiting_reg_approval': awaiting_reg_approval,
        'schedules_count': schedules_count,
        'current_schedules_count': current_schedules_count,
    }
    return render(request, 'monitoring/monitoring_dashboard.html', context)



@login_required
def upload_internship_centers(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('monitoring:monitoring_dashboard')
    else:
        form = DocumentForm()
    return render(request, 'monitoring/internship_centers.html', {
        'form': form
    })




class HospitalUploadListView(StaffRequiredMixin, ListView):
    template_name = "monitoring/hospitals_upload_list.html"
    def get_queryset(self):
        # request = self.request
        # user = request.user
        qs = Hospital.objects.filter(application_status = 1).order_by('-date')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs 



class HospitalsUpdatedUploadListView(StaffRequiredMixin, ListView):
    template_name = "monitoring/hospitals_upload_list.html"
    def get_queryset(self):
        # request = self.request
        # user = request.user
        qs = Hospital.objects.filter(application_status = 2).order_by('-date')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs 

class UploadInternshipList1(StaffRequiredMixin, View):
    def get(self, request):
        internship_list = InternshipList.objects.all()
        return render(self.request, 'monitoring/file_upload.html', {'list': internship_list})

    def post(self, request):
        form = InternshipListForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            document = form.save()
            data = {'is_valid': True, 'name': document.file.name, 'url': document.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)

class UploadInternshipList(StaffRequiredMixin, View):
    def get(self, request):
        internship_list = InternshipList.objects.all()
        return render(self.request, 'monitoring/file_upload.html', {'list': internship_list})

    def post(self, request):
        time.sleep(1)
        form = InternshipListForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            document = form.save()
            data = {'is_valid': True, 'name': document.file.name, 'url': document.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


@login_required
def clear_database(request):
    for document in InternshipList.objects.all():
        document.file.delete()
        document.delete()
    return redirect(request.POST.get('next'))

class MyUserAccount(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'monitoring/my_profile.html')

def downloadfile(request):
     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
     filename = 'hospital_list.csv'
     filepath = base_dir + '/static/csv/' + filename
     thefile = filepath
     filename = os.path.basename(thefile) 
     chunk_size = 8192
     response = StreamingHttpResponse(FileWrapper(open(thefile, 'rb'),chunk_size), content_type=mimetypes.guess_type(thefile)[0])
     response['Content-Length'] = os.path.getsize(thefile)
     response['Content-Disposition'] = "Attachment;filename=%s" % filename
     return response


class HospitalProfileCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    form = HospitalProfileModelForm
    def get(self, request, *args, **kwargs):
        form = HospitalProfileModelForm()
        template_name = 'monitoring/bulk_create_hospitals.html'
        return render(request, template_name, {'form':form})
 
    # def get_context_data(self, request, *args, **kwarg):
    #     user = self.request.user
    #     form = HospitalProfileModelForm()
    #     qs1 = Hospital.objects.filter(name=user.get_indexing_officer_profile.institution)
    #     obj = qs1.first().studentprofile_set.all()
    #     context['object'] = obj
    #     context['form'] = form
            
    def post(self, request, *args, **kwargs):
        # user = self.request.user
        # institution = Hospital.objects.filter(name=user.get_indexing_officer_profile.institution).first()
        # print("Institution:", institution)
        # session = request.POST.get('academic_session')
        # academic_session = AcademicSession.objects.get(id=session)
        # print("Academic Session:", academic_session)
        # quota = AdmissionQuota.objects.get_or_none(institution = institution, academic_session = academic_session)
        # print("Quota:", quota)
        # if quota is None:
        #     admission_quota = 0;
        # else:
        #     admission_quota = quota.admission_quota
        # print("Admission Quota:", admission_quota)
        # students_qs = institution.studentprofile_set.all()

        # students_list = students_qs.filter(academic_session = academic_session)
        paramFile = io.TextIOWrapper(request.FILES['hospitals_list'].file)
        portfolio1 = csv.DictReader(paramFile)
        list_of_dict = list(portfolio1)

        try:
            context = {}
            # if admission_quota == 0:
            #     messages.error(request, "No Quota Assigned for Selected Academic Session")
            #     print("Number in List:",  len(list_of_dict))
            #     print("Number of students registered:", len(students_list))
            #     print("Admission Quota:", int(admission_quota))
            #     return redirect("monitoring:create_hospital_profile")

            # elif len(students_list) > admission_quota or len(list_of_dict) > admission_quota or len(list_of_dict) + int(len(students_list)) > admission_quota:
            #     messages.error(request, "Admission Quota exceeded!")
            #     print("Number in List:",  len(list_of_dict))
            #     print("Number of students registered:", len(students_list))
            #     print("Admission Quotas:", int(admission_quota))
            #     return redirect("monitoring:create_hospital_profile")

            # else:
            
            for row in list_of_dict:
                data = row['email']
                # hospital_name = row['hospital_name']
                # phone_no = row['phone_no']
                hospitals_list = User.objects.filter(email = data)
                # print("Students:", students_list)
                try:
                    if hospitals_list.exists():
                        for hospital_admin in hospitals_list:
                            messages.error(request, f'This User: {hospital_admin} and possibly other users on this list exit already exist')
                        return redirect("monitoring:create_hospital_profile")
                    else:
                        hospital_admin = User.objects.create(email=row['email'], last_name=row['last_name'], first_name=row['first_name'], is_active = True, hospital = True, password = make_password('rrbnhq123%'),)
                        
                except Exception as e:
                    messages.error(request, e)

            objs = [
                Hospital(
                    hospital_admin = User.objects.get(email=row['email']),
                    type = request.POST['type'],
                    hospital_name = row['hospital_name'],
                    phone_no = row['phone_no'],
                )
                for row in list_of_dict     
             ]
            # for obj in objs:
            #     obj.slug = create_slug3(instance=obj)
            nmsg = Hospital.objects.bulk_create(objs)
            messages.success(request, "Bulk Creation of Hospitals successful!")
            returnmsg = {"status_code": 200}
            for obj in objs:
                user = obj.hospital_admin
                print("User:", user)
                # reset_password(user, request)
            # return redirect(institution.first().get_student_profiles_list())
            return redirect("monitoring:create_hospital_profile")          
        except Exception as e:
            print('Error While Importing Data: ', e)
            returnmsg = {"status_code": 500}
        return JsonResponse(returnmsg)


class HospitalProfileListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/hospital_profile_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        # request = self.request
        # user = request.user
        qs = Hospital.objects.filter(application_status = 1).order_by('-date')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs 

class InspectionScheduleListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspection_schedule_list.html'
    paginate_by = 10  # Default items per page

    def get_queryset(self):
        """
        Combine two querysets filtering payments based on specific conditions
        and return as a list to support pagination.
        """
        payment_qs = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Radiography Practice Permit',
            hospital__application_type='New Registration - Radiography Practice Permit',
        )
        payment_qss = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Internship Accreditation',
        )
        # Combine querysets and convert to list
        return list(chain(payment_qs, payment_qss))

    def get_context_data(self, **kwargs):
        """
        Add additional context data, including paginated combined payments.
        """
        context = super().get_context_data(**kwargs)

        combined_payments = self.get_queryset()  # Get the combined queryset
        paginator = Paginator(combined_payments, self.paginate_by)  # Handle pagination
        page_number = self.request.GET.get('page')  # Get the current page number
        page_obj = paginator.get_page(page_number)  # Get the appropriate page

        # Add pagination context
        context['page_obj'] = page_obj
        context['combined_payments'] = page_obj.object_list  # Paginated objects

        return context



class AllHospitalsView(LoginRequiredMixin, ListView):
    template_name = "monitoring/hospitals_applications_table.html"
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user

        # Fetch related data from models with annotations
        models = [
            # (Hospital, "Hospital"),
            (Document, "Document"),
            (Payment, "Payment"),
            (Schedule, "Schedule"),
            (Inspection, "Inspection"),
            (License, "License"),
            (Appraisal, "Internship"),
        ]
        querysets = [
            model.objects.annotate(model_name=Value(name, output_field=CharField()))
            for model, name in models
        ]

        combined_qs = list(chain(*querysets))

        # Priority mapping for sorting
        model_priority = {
            "Hospital": 7,
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
        context["applications"] = applications 
        return context


class AllHospitalsView00(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/hospitals_application_table2.html"
    context_object_name = "all_hospitals_list"

    def get_queryset(self):
        # Consolidate stages into a single queryset with annotations
        stages = list(chain(
            Hospital.objects.filter(application_status=1),
            Document.objects.filter(application_status=1),
            Payment.objects.filter(application_status=2),
            Schedule.objects.filter(application_status=4),
            Inspection.objects.filter(application_status=5),
            Appraisal.objects.filter(application_status=5),
            License.objects.filter(application_status=8),
        ))
        # Sort by primary key (or date if applicable)
        return sorted(stages, key=lambda instance: instance.pk, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter hospitals by type for specific categories
        hospital_types = {
            "hospital_rpp": "Radiography Practice Permit",
            "hospital_gia": "Gov Internship Accreditation",
            "hospital_pia": "Pri Internship Accreditation",
            "hospital_rppr": "Radiography Practice Permit Renewal",
            "hospital_piar": "Pri Internship Accreditation Renewal",
            "hospital_giar": "Gov Internship Accreditation Renewal",
        }

        for key, hospital_type in hospital_types.items():
            context[key] = Hospital.objects.filter(
                application_status=1, type=hospital_type
            )

        # General stage filtering
        context["stage_one"] = Hospital.objects.filter(application_status=1)
        context["stage_two"] = Document.objects.filter(application_status=1)
        context["stage_three"] = Payment.objects.filter(application_status=2)
        context["stage_four"] = Payment.objects.filter(application_status=3)
        context["stage_five"] = Schedule.objects.filter(application_status=4)
        context["stage_six"] = Inspection.objects.filter(application_status=5)
        context["stage_seven"] = Appraisal.objects.filter(application_status=5)
        context["stage_eight"] = Inspection.objects.filter(application_status=6)
        context["stage_nine"] = Appraisal.objects.filter(application_status=6)
        context["stage_ten"] = Inspection.objects.filter(application_status=7)
        context["stage_eleven"] = Appraisal.objects.filter(application_status=7)
        context["stage_twelve"] = License.objects.filter(application_status=8)

        return context



class AllHospitalsView1(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/hospitals_application_table2.html"
    context_object_name = 'object'
    # model = Document 

    def get_queryset(self):
         queryset = Document.objects.order_by('-date')
         return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super(AllHospitalsView, self).get_context_data(**kwargs)
        hospital_rpp = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Radiography Practice Permit')
        context['hospital_rpp'] = hospital_rpp
        hospital_gia = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Gov Internship Accreditation')
        hospital_pia = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Pri Internship Accreditation')
        hospital_rppr = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Radiography Practice Permit Renewal')
        hospital_piar = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Pri Internship Accreditation Renewal')
        hospital_giar = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Gov Internship Accreditation Renewal')
        
        stage_one = Hospital.objects.select_related("hospital_admin").filter(application_status=1)
        context['stage_one'] = stage_one


        document_rpp = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Radiography Practice Permit', application_type = 'New Registration - Radiography Practice Permit')
        context['document_rpp'] = document_rpp
        document_gia = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Government Hospital Internship')
        document_pia = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Private Hospital Internship')
        document_rppr = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Radiography Practice Permit', application_type = 'Renewal - Radiography Practice Permit')
        document_piar = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Private Hospital Internship')
        document_giar = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Government Hospital Internship')
       
        stage_two = Document.objects.select_related("hospital_name").filter(application_status=1)
        context['stage_two'] = stage_two


        payment_rpp = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        payment_gia = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        payment_pia = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        payment_rppr = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        payment_piar = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        payment_giar = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_three = Payment.objects.select_related("hospital_name").filter(application_status=2)
        context['stage_three'] = stage_three

        payment_vrpp = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        payment_vgia = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        payment_vpia = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        payment_vrppr = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        payment_vpiar = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        payment_vgiar = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_four = Payment.objects.select_related("hospital_name").filter(application_status=3)
        context['stage_four'] = stage_four

        schedule_rpp = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        schedule_gia = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        schedule_pia = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        schedule_piar = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        schedule_giar = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_five = Schedule.objects.select_related("hospital_name").filter(application_status=4)
        context['stage_five'] = stage_five

        inspection_rpp = Inspection.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        accreditation_gia = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        accreditation_pia = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #inspection_qsr = Inspection.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        accreditation_piar = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        accreditation_giar = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        
        stage_six = Inspection.objects.select_related("hospital_name").filter(application_status=5)
        context['stage_six'] = stage_six

        stage_seven = Appraisal.objects.select_related("hospital_name").filter(application_status=5)
        context['stage_seven'] = stage_seven


        inspection_arpp = Inspection.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        accreditation_agia = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        accreditation_apia = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['inspection_approved_qsr'] = Inspection.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        accreditation_apiar = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        accreditation_agiar = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_eight = Inspection.objects.select_related("hospital_name").filter(application_status=6)
        context['stage_eight'] = stage_eight

        stage_nine = Appraisal.objects.select_related("hospital_name").filter(application_status=6)
        context['stage_nine'] = stage_nine


        registrar_arpp = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        registrar_agia = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        registrar_apia = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['registrar_approval_qsr'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        registrar_arppr = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        registrar_apiar = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        registrar_agiar = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_ten = Inspection.objects.select_related("hospital_name").filter(application_status=7)
        context['stage_ten'] = stage_ten

        stage_eleven = Appraisal.objects.select_related("hospital_name").filter(application_status=7)
        context['stage_eleven'] = stage_eleven


        license_irpp = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        license_igia = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        license_ipia = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        license_irppr = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        license_ipiar = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        license_igiar = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_twelve = License.objects.select_related("hospital_name").filter(application_status=8)
        context['stage_twelve'] = stage_twelve
        
        all_hospitals_list = sorted(chain(stage_one, stage_two, stage_three, stage_four, stage_five, stage_six, stage_seven, stage_eight, stage_nine, stage_ten, stage_eleven, stage_twelve), key=lambda instance: instance.pk,reverse=True)

        # all_hospitals_list = sorted(chain(hospital_rpp, hospital_gia, hospital_pia, hospital_rppr, hospital_piar, hospital_giar, document_rpp, document_gia, document_pia, document_rppr, document_piar, document_giar, payment_rpp, payment_gia, payment_pia, payment_rppr, payment_piar, payment_giar, payment_vrpp, payment_vgia, payment_vpia, payment_vrppr, payment_vpiar, payment_vgiar, schedule_rpp, schedule_gia, schedule_pia, schedule_piar, schedule_pia, schedule_piar, schedule_giar, inspection_rpp, accreditation_gia, accreditation_pia, accreditation_piar, accreditation_giar, inspection_arpp, accreditation_agia, accreditation_apia, accreditation_apiar, accreditation_agiar, registrar_arpp, registrar_agia, registrar_apia, registrar_arppr, registrar_apiar, registrar_agiar, license_irpp, license_igia, license_ipia, license_irppr, license_ipiar, license_igiar), key=lambda instance: instance.date,reverse=True)
        context['all_hospitals_list'] = all_hospitals_list
        return context 


class NewHospitalProfileDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/new_hospital_profile_details.html"
    model = Hospital



class UpdateHospitalProfileDetails (StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    user_form = UserUpdateForm
    form = HospitalProfileModelForm
    template_name = "monitoring/update_hospital_profile_details.html"

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
    # success_message = "Student Profile Update Successful"

    success_message = "%(hospital_admin)s  Hospital Profile Update Successful"
    
    def get_success_message(self, cleaned_data):
      return self.success_message % dict(
            cleaned_data,
            hospital_admin=self.object.hospital_admin.get_full_name(),
        )

    def get_success_url(self):
        return reverse("monitoring:hospitals_upload_list") 


    def post(self, request, *args, **kwargs):
        # email = request.POST['email']
        # pk = self.kwargs.get("pk")
        # obj = get_object_or_404(User, id=pk)
        # obj = StudentProfile.objects.get(student__email= form.cleaned_data["email"]).student.email
        obj = self.get_object()
        user = User.objects.filter(email=obj.hospital_admin.email).first()
        print("User1:", user)
        print("Object:", obj)

        form = HospitalProfileModelForm(request.POST or None, instance=obj)
        user_form = UserUpdateForm(request.POST or None, instance=user)
        for field in form:
            print("Field Error:", field.name,  field.errors)


        for field in user_form:
            print("Field Error:", field.name,  field.errors)

        print ("Valid:", user_form.is_valid())
        print ("Form Valid:", form.is_valid())
        if user_form.is_valid() and form.is_valid():
            print ("Valid:", user_form.is_valid())
            hospital_profile = form.save(commit = False)
            if hospital_profile.application_status >2:
                pass
            else:
                hospital_profile.application_status = 2
            hospital_profile.save()
            

            user = user_form.save(commit=False)
            user.is_active = True  # Deactivate account till it is confirmed
            user.hospital = True
            user.set_password('rrbnhq123%') 
            # user.password = make_password('rrbnhq123%') 
            user.save()
            hospital = Hospital.objects.filter(hospital_admin=user).first()        
            # reset_password(user, request)
            # reset_user_password(user, self.request)
            messages.success(request, 'Hospital Profile Update Successful')
            return redirect(hospital.get_absolute_url())
        else:
            messages.error(request, 'Hospital Profile Update Failed.')
            hospital = Hospital.objects.filter(hospital_admin=user).first() 
            return redirect(hospital.get_absolute_url())
        return super(UpdateHospitalProfileDetails, self).form_valid(form and user_form)






class UpdateHospitalProfileDetails1 (StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SignupForm
    template_name = "monitoring/update_hospital_profile_details.html"
    # success_message = "Student Profile Update Successful"

    success_message = "%(student)s  Hospital Profile Update Successful"
    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        user = User.objects.get(id=pk)
        return user

    def get_success_message(self, cleaned_data):
      return self.success_message % dict(
            cleaned_data,
            student=self.object.get_full_name,
        )

    def get_success_url(self):
        return reverse("monitoring:hospitals_upload_list") 


    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(User, id=pk)
        # obj = StudentProfile.objects.get(student__email= form.cleaned_data["email"]).student.email
        form = self.form_class(request.POST or None, instance = obj)
        if form.is_valid():
            hospital_profile = form.save()
            user = hospital_profile
            hospital_profile = Hospital.objects.filter(hospital_admin=user).first()
            print("User:", user)
            # reset_password(user, request)
            # reset_user_password(user, self.request)
            messages.success(request, 'Hospital Profile Update Successful')
            return redirect(hospital_profile.get_absolute_url())
        else:
            messages.error(request, 'The email you are trying to assign to this user is already in use')
            user = get_object_or_404(User, id=pk)
            hospital_profile = Hospital.objects.filter(hospital_admin=user).first()
            return redirect(hospital_profile.get_absolute_url())
        return super(UpdateHospitalProfileDetails, self).form_valid(form)




class HospitalProfileDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_profile_details.html"
    model = Hospital

class HospitalRegistrationDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_registration_details.html"
    model = Document

class HospitalPaymentDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_payment_details.html"
    model = Payment


class HospitalVerificationDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_verification_details.html"
    model = Payment

class HospitalScheduleDetails(StaffRequiredMixin,LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_schedule_details.html"
    model = Schedule

class HospitalInspectionDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_details.html"
    model = Inspection

class HospitalAccreditationDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_details.html"
    model = Appraisal


class HospitalInspectionApprovalDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_approval_details.html"
    model = Inspection


class HospitalAccreditationApprovalDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_approval_details.html"
    model = Appraisal

class HospitalInspectionRegistrarApprovalDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_registrar_approval_details.html"
    model = Inspection

class HospitalAccreditationRegistrarApprovalDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_registrar_approval_details.html"
    model = Appraisal
    

class HospitalLicenseDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_license_details.html"
    model = License


class RegistrationListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/list-applications.html"
    context_object_name = 'object'


    def get_queryset(self):
        return Payment.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(RegistrationListView, self).get_context_data(**kwargs)
        obj['registration_list_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=1)
        #obj['hospital'] = Document.objects.filter(application_no=self.object_list)
        #self.document = Document.objects.get(pk=self.kwargs['pk'])
        return obj

class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


#class VetApplication(LoginRequiredMixin, DetailView):
    #template_name = "monitoring/view-applications2.html"
    #model = Payment
    
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['payment'] = Document.objects.all()
        #context['hospital'] = Hospital.objects.all()
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #return context


#class VetApplication(LoginRequiredMixin, PaymentObjectMixin, View):
    #template_name = "monitoring/view-applications2.html"

    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #context['object'] = obj
        #context['registration'] = Document.objects.filter (application_no=obj.application_no)
        #return render(request, self.template_name, context) 

class VetApplication(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "monitoring/vet_application.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)  

# @login_required
# def approve(request, id):
#   if request.method == 'POST':
#      object = get_object_or_404(Payment, pk=id)
#      object.hospital_name.application_status = 3
#      object.vet_status = 2
#      object.application_status = 3
#      object.vetting_officer = request.user
#      object.vet_date = date.today
#      object.save()
#      context = {}
#      context['object'] = object
#      context['registration'] = Document.objects.filter (application_no=object.application_no)
#      subject = 'Successful verification of Registration and Payment Details'
#      from_email = settings.DEFAULT_FROM_EMAIL
#      to_email = [object.hospital_name.hospital_admin]
#      contact_message = get_template('monitoring/contact_message.txt').render(context)
#      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
#      messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection in case of New Practice Permit Application or Internship Accreditation Application.'))
#      return render(request, 'monitoring/verification_successful.html',context)

@login_required
def approve(request, id):
    if request.method == 'POST':
        # Retrieve and update the Payment object
        payment = get_object_or_404(Payment, pk=id)
        payment.hospital_name.application_status = 3
        payment.vet_status = 2
        payment.application_status = 3
        payment.vetting_officer = request.user
        payment.vet_date = date.today()
        payment.save()

        # Prepare context for the email and rendering
        context = {
            'object': payment,
            'registration': Document.objects.filter(application_no=payment.application_no),
        }

        # Email details
        subject = 'Successful Verification of Registration and Payment Details'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [payment.hospital_name.hospital_admin]
        contact_message = get_template('monitoring/contact_message.txt').render(context)

        # Send the email
        try:
            send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
            # return render(request, 'monitoring/verification_failed.html', context)
            return render(request, 'monitoring/verification_successful.html', context)

        # Success message and response
        messages.success(request, (
            "Application vetted successfully. Please proceed to Schedule Hospital for Inspection in case "
            "of New Practice Permit Application or Internship Accreditation Application."
        ))
        return render(request, 'monitoring/verification_successful.html', context)

    # Handle non-POST requests (optional)
    messages.error(request, "Invalid request method.")
    return render(request, 'monitoring/verification_failed.html')



# @login_required 
# def reject_application(request, id):
#   if request.method == 'POST':
#      object = get_object_or_404(Payment, pk=id)
#      object.vet_status = 3
#      object.save()
#      context = {}
#      context['object'] = object
#      subject = 'Failed verification of Registration and Payment Details'
#      from_email = settings.DEFAULT_FROM_EMAIL
#      to_email = [object.hospital_name.hospital_admin] 
#      contact_message = get_template('monitoring/verification_failed.txt').render(context)
#      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
#      messages.error(request, ('Verification failed.  Hospital has been sent an email to re-apply with the correct details.'))
#      return redirect('/monitoring/'+str(object.id))


@login_required 
def reject_application(request, id):
    if request.method == "POST":
        application = get_object_or_404(Payment, pk=id)
        rejection_reason = request.POST.get("rejection_reason")

        # Save the rejection reason to the application
        application.vet_status = 3
        application.is_rejected = True
        application.rejection_reason = rejection_reason
        application.application_status = 3
        application.vetting_officer = request.user
        application.save()

        messages.error(request, "Application rejected with reason: " + rejection_reason)
        return redirect("monitoring:rejection_details", id=application.id)



# def reject_application(request, application_id):
#     if request.method == "POST":
#         application = get_object_or_404(Application, id=application_id)
#         rejection_reason = request.POST.get("rejection_reason")

#         # Save the rejection reason to the application
#         application.is_rejected = True
#         application.rejection_reason = rejection_reason
#         application.save()

#         messages.error(request, "Application rejected with reason: " + rejection_reason)
#         return redirect("monitoring:application_list")




def rejection_details(request, id):
    object = get_object_or_404(Payment, pk=id)
    return render(request, "monitoring/application_rejected.html", {"object": object})



class RegistrationObjectMixin(object):
    model = Document
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class InspectionScheduleListView2(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspection_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Payment.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(InspectionScheduleListView, self).get_context_data(**kwargs)
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Internship Accreditation')
        return context





class InspectionScheduleListView1(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspection_schedule_list.html'
    
    def get_queryset(self):
        # Combine both querysets into one
        payment_qs = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Radiography Practice Permit',
            hospital__application_type='New Registration - Radiography Practice Permit',
        )
        payment_qss = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Internship Accreditation',
        )
        return list(payment_qs) + list(payment_qss)  # Combine both querysets
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_payments'] = self.get_queryset()  # Pass combined queryset
        return context



class InspectionScheduleListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspection_schedule_list.html'
    paginate_by = 10  # Default items per page

    def get_queryset(self):
        """
        Combine two querysets filtering payments based on specific conditions
        and return as a list to support pagination.
        """
        payment_qs = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Radiography Practice Permit',
            hospital__application_type='New Registration - Radiography Practice Permit',
        )
        payment_qss = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital__license_type='Internship Accreditation',
        )
        # Combine querysets and convert to list
        return list(chain(payment_qs, payment_qss))

    def get_context_data(self, **kwargs):
        """
        Add additional context data, including paginated combined payments.
        """
        context = super().get_context_data(**kwargs)

        combined_payments = self.get_queryset()  # Get the combined queryset
        paginator = Paginator(combined_payments, self.paginate_by)  # Handle pagination
        page_number = self.request.GET.get('page')  # Get the current page number
        page_obj = paginator.get_page(page_number)  # Get the appropriate page

        # Add pagination context
        context['page_obj'] = page_obj
        context['combined_payments'] = page_obj.object_list  # Paginated objects

        return context



#class InspectionCreateView(LoginRequiredMixin, PaymentObjectMixin, View):
    #template_name = 'monitoring/schedule_inspection.html'
    #template_name1 = 'monitoring/inspection_scheduled.html'
    #def get(self, request,  *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = ScheduleModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form

        #return render(request, self.template_name, context)

   
    #def post(self, request,  *args, **kwargs):
        #form = ScheduleModelForm(request.POST)
        #if form.is_valid():
            #form.save()

        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form
           #hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)

           #subject = 'Notice of Facility Inspection'
           #from_email = settings.DEFAULT_FROM_EMAIL
           #to_email = [hospital_admin]

           #context['form'] = form
           #contact_message = get_template(
               #'monitoring/inspection_details.txt').render(context)

           #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)  
        
        #return render(request, self.template_name1, context)




class InspectionScheduleCreateView1(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit', application_no=self.payment.application_no)
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', application_no=self.payment.application_no)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'payment': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        kwargs['initial']['application_no'] = self.payment.application_no  
        return kwargs
      

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())



class InspectionScheduleCreateView(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Combine the querysets into one list
        combined_payments = Payment.objects.select_related("hospital_name").filter(
            vet_status=2,
            hospital_name=self.payment.hospital_name,
            application_no=self.payment.application_no,
        ).filter(
            Q(hospital__license_type='Radiography Practice Permit', hospital__application_type='New Registration - Radiography Practice Permit') |
            Q(hospital__license_type='Internship Accreditation')
        )
        context['combined_payments'] = combined_payments
        
        return context

    def get_initial(self):
        return {
            'payment': self.kwargs["pk"],
        }


    def form_valid(self, form):
        # Debug: Print POST data
        print("POST Data:", self.request.POST)
        for i in range(1, 7):
            name_key = f'inspector{i}_name'
            phone_key = f'inspector{i}_phone'
            name = self.request.POST.get(name_key)
            phone = self.request.POST.get(phone_key)
            print(f"{name_key}: {name}, {phone_key}: {phone}")

        # Save the main form
        self.object = form.save(commit=False)
        
        # Manually assign additional inspector fields
        for i in range(1, 7):  # Inspectors 1 to 6
            name_key = f'inspector{i}_name'
            phone_key = f'inspector{i}_phone'
            name = self.request.POST.get(name_key)
            phone = self.request.POST.get(phone_key)
            
            if name and phone:
                setattr(self.object, name_key, name)
                setattr(self.object, phone_key, phone)
            elif i == 1:
                # Inspector 1 is required
                messages.error(self.request, "Inspector 1 details are required.")
                return self.form_invalid(form)
        
        self.object.save()  # Save the Schedule instance with inspector details
        return super().form_valid(form)

    def get_form_kwargs(self):
        # Use get_object_or_404 for safety
        kwargs = super().get_form_kwargs()
        self.payment = get_object_or_404(Payment, pk=self.kwargs['pk']) 
        # zone = self.request.GET.get('inspection_zone')  # Get zone from request
        # kwargs['zone'] = zone  
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        kwargs['initial']['application_no'] = self.payment.application_no  
        return kwargs

    def form_invalid(self, form):
        # Render the form with errors and context data
        print("Form errors:", form.errors)
        messages.error(self.request, "There was an error with your submission. Please review and try again.")
        return self.render_to_response(self.get_context_data(form=form))


@login_required

def get_inspectors_by_zone_htmx(request):
    zone = request.GET.get('inspection_zone')
    if zone:
        inspectors = Inspector.objects.filter(zone=zone)  # Filter inspectors by the selected zone
    else:
        inspectors = []
    # inspectors = Inspector.objects.filter(zone=zone) if zone else []
    print("Inspection Zone:", zone)
    print("Inspectors:", inspectors)
    print("Request GET:", request.GET)
    print("Request GET Zone:", request.GET.get('zone'))
    # return render(request, 'partials/inspectors_dropdown.html', {'inspectors': inspectors})
    return render(request, 'partials/inspectors_checkboxes.html', {'inspectors': inspectors, 'zone':zone })





class AppraisalCreateView(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship', application_no=self.payment.application_no)
        context['payment_qsss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship', application_no=self.payment.application_no)
        #context['payment_qsr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit', application_no=self.payment.application_no)
        context['payment_qssr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship', application_no=self.payment.application_no)
        context['payment_qgssr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship', application_no=self.payment.application_no)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'payment': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        kwargs['initial']['application_no'] = self.payment.application_no
        #kwargs['initial']['hospital'] = self.payment.hospital
        
        return kwargs
      

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class ScheduleObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionCreateDetailView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Schedule
    template_name = "monitoring/inspection_scheduled.html"
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inspectors = [
            {"name": self.object.inspector1_name, "phone": self.object.inspector1_phone},
            {"name": self.object.inspector2_name, "phone": self.object.inspector2_phone},
            {"name": self.object.inspector3_name, "phone": self.object.inspector3_phone},
            {"name": self.object.inspector4_name, "phone": self.object.inspector4_phone},
            {"name": self.object.inspector5_name, "phone": self.object.inspector5_phone},
            {"name": self.object.inspector6_name, "phone": self.object.inspector6_phone},
        ]
        # Filter out empty entries
        context['approved_inspectors'] = [inspector for inspector in inspectors if inspector['name'] and inspector['phone']]
        return context


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['inspectors'] = self.object.inspectors.all()
    #     return context

class InspectionCreateDetailView1(StaffRequiredMixin, LoginRequiredMixin, ScheduleObjectMixin, View):
    template_name = 'monitoring/inspection_scheduled.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspectors'] = self.object.inspectors.all()
        return context

    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = ScheduleModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
            subject = 'Notice of Facility Inspection'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]
            context['form'] = form
            contact_message = get_template(
               'monitoring/inspection_details.txt').render(context)
            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)



class ScheduledInspectionsListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/scheduled_inspections_list.html"
    context_object_name = "combined_records"

    def get_queryset(self):
        schedules = Schedule.objects.select_related("hospital").all()
        inspections = Inspection.objects.select_related("hospital").all()
        appraisals = Appraisal.objects.select_related("hospital").all()

        # Convert QuerySets to dictionaries for fast lookup
        inspection_map = {insp.schedule_id: insp for insp in inspections}
        appraisal_map = {appr.schedule_id: appr for appr in appraisals}

        final_records = []  # Prevents duplicates

        # Process schedules and merge related inspections and appraisals
        for schedule in schedules:
            schedule.is_inspection = schedule.id in inspection_map
            schedule.is_appraisal = schedule.id in appraisal_map
            schedule.is_pending = not (schedule.is_inspection or schedule.is_appraisal)

            # Attach related inspection and appraisal details to schedule object
            schedule.inspection_date = inspection_map[schedule.id].inspection_date if schedule.is_inspection else None
            schedule.appraisal_date = appraisal_map[schedule.id].appraisal_date if schedule.is_appraisal else None

            final_records.append(schedule)

        # Sort with pending schedules first
        combined_records = sorted(final_records, key=lambda obj: obj.is_pending, reverse=True)

        return combined_records


class ScheduledInspectionsListView0(LoginRequiredMixin, ListView):
    template_name = "monitoring/scheduled_inspections_list.html"
    context_object_name = "combined_records"

    def get_queryset(self):
        schedules = Schedule.objects.select_related("hospital").all()
        inspections = Inspection.objects.select_related("hospital").all()
        appraisals = Appraisal.objects.select_related("hospital").all()

        # Convert QuerySets to dictionaries for quick lookup
        inspection_ids = {insp.schedule_id for insp in inspections}
        appraisal_ids = {appr.schedule_id for appr in appraisals}

        # Add flags to each object
        for obj in schedules:
            obj.is_schedule = True
            obj.is_inspection = obj.id in inspection_ids
            obj.is_appraisal = obj.id in appraisal_ids
            obj.is_pending = not obj.is_inspection and not obj.is_appraisal  # True if neither exist

        for obj in inspections:
            obj.is_schedule = True
            obj.is_inspection = True
            obj.is_appraisal = False
            obj.is_pending = False  # Inspections are never pending

        for obj in appraisals:
            obj.is_schedule = True
            obj.is_inspection = False
            obj.is_appraisal = True
            obj.is_pending = False  # Appraisals are never pending

        # Combine into a single iterable
        combined_records = sorted(
            chain(schedules, inspections, appraisals),
            key=lambda obj: not obj.is_pending  # Sorts `is_pending=True` first
        )

        return combined_records






class ScheduledInspectionsListView1(LoginRequiredMixin, ListView):
    template_name = "monitoring/scheduled_inspections_list.html"
    context_object_name = 'combined_records'

    def get_queryset(self):
        # Fetch schedules, inspections, and appraisals
        schedules = Schedule.objects.select_related('hospital').all()
        inspections = Inspection.objects.select_related('hospital').all()
        appraisals = Appraisal.objects.select_related('hospital').all()

        # Combine the querysets into one iterable using chain
        combined_records = chain(schedules, inspections, appraisals)
        return combined_records

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_records'] = self.get_queryset()  # Combined records
        return context




class InspectionCompletedListView4(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_lists.html'

    def get_queryset(self):
        inspections = Inspection.objects.annotate(
            appraisal_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for appraisal status
        ).select_related("hospital_name").filter(vet_status=4)

        appraisals = Appraisal.objects.annotate(
            inspection_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for inspection status
        ).select_related("hospital_name").filter(vet_status=4)

        return list(inspections) + list(appraisals)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_records'] = self.get_queryset()
        return context




class InspectionCompletedListView00(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_lists.html'
    context_object_name = 'combined_records'

    def get_queryset(self):
        # Fetch completed inspections and provide a placeholder for appraisal status
        inspections = Inspection.objects.filter(vet_status=4).select_related("hospital_name").annotate(
            appraisal_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for appraisals
        )

        # Fetch completed appraisals and provide a placeholder for inspection status
        appraisals = Appraisal.objects.filter(vet_status=4).select_related("hospital_name").annotate(
            inspection_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for inspections
        )

        # Combine records
        combined_records = list(chain(inspections, appraisals))

        # Sort by pending status (1 = Pending, others follow)
        sorted_records = sorted(
            combined_records,
            key=lambda obj: 0 if (
                getattr(obj, "inspection_status", None) == 1 or 
                getattr(obj, "appraisal_status", None) == 1
            ) else 1
        )

        return sorted_records

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["combined_records"] = self.get_queryset()
        return context


class InspectionCompletedListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_lists.html'
    context_object_name = 'combined_records'

    def get_queryset(self):
        # Fetch completed inspections and provide a placeholder for appraisal status
        inspections = Inspection.objects.filter(vet_status=4).select_related("hospital_name").annotate(
            appraisal_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for appraisals
        )

        # Fetch completed appraisals and provide a placeholder for inspection status
        appraisals = Appraisal.objects.filter(vet_status=4).select_related("hospital_name").annotate(
            inspection_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for inspections
        )

        # Combine records
        combined_records = list(chain(inspections, appraisals))

        # Sort by most recent date (inspection_date or appraisal_date)
        sorted_records = sorted(
            combined_records,
            key=lambda obj: getattr(obj, "inspection_date", None) or getattr(obj, "appraisal_date", None) or now(),
            reverse=True  # Ensures descending order (most recent first)
        )

        return sorted_records

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["combined_records"] = self.get_queryset()
        return context




class InspectionCompletedListView3(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_list.html'

    def get_queryset(self):
        inspections = Inspection.objects.annotate(
            appraisal_status=Value(None)  # Add a placeholder for objects without appraisal_status
        ).select_related("hospital_name").filter(vet_status=4)

        appraisals = Appraisal.objects.annotate(
            inspection_status=Value(None)  # Add a placeholder for objects without inspection_status
        ).select_related("hospital_name").filter(vet_status=4)

        return list(inspections) + list(appraisals)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_records'] = self.get_queryset()
        return context

class InspectionCompletedListView2(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_lists.html'
    context_object_name = 'combined_records'

    def get_queryset(self):
        # Fetch completed inspections
        inspection_qs = Inspection.objects.select_related("hospital_name").filter(vet_status=4)
        # Fetch completed appraisals
        appraisal_qs = Appraisal.objects.select_related("hospital_name").filter(vet_status=4)
        # Combine both querysets using chain
        return list(chain(inspection_qs, appraisal_qs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        combined_qs = self.get_queryset()
        context['combined_qs'] = combined_qs
        # Pass additional context if needed
        context['inspection_count'] = sum(1 for obj in combined_qs if isinstance(obj, Inspection))
        context['appraisal_count'] = sum(1 for obj in combined_qs if isinstance(obj, Appraisal))
        
        return context


class InspectionCompletedListView1(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()
    def get_context_data(self, **kwargs):
        obj = super(InspectionCompletedListView, self).get_context_data(**kwargs)
        obj['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(vet_status=4)
        #obj['inspections_qs'] = Inspection.objects.all()
        obj['appraisal_qs'] = Appraisal.objects.select_related("hospital_name").filter(vet_status=4)
        #obj['appraisals_qs'] = Appraisal.objects.all()   
        return obj                 



class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AccreditationObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AccreditationCompletedDetailView1(StaffRequiredMixin, LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = "monitoring/appraisals_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)

class InspectionCompletedDetailView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Inspection
    template_name = "monitoring/inspections_detail.html" # DetailView
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Additional context or derived data
        inspection = self.object
        inspectors = [
            {"name": self.object.schedule.inspector1_name, "phone": self.object.schedule.inspector1_phone},
            {"name": self.object.schedule.inspector2_name, "phone": self.object.schedule.inspector2_phone},
            {"name": self.object.schedule.inspector3_name, "phone": self.object.schedule.inspector3_phone},
            {"name": self.object.schedule.inspector4_name, "phone": self.object.schedule.inspector4_phone},
            {"name": self.object.schedule.inspector5_name, "phone": self.object.schedule.inspector5_phone},
            {"name": self.object.schedule.inspector6_name, "phone": self.object.schedule.inspector6_phone},
        ]
        context['photos'] = [
            {'label': 'Main Photo', 'image': inspection.photo_main} if inspection.photo_main else None,
            {'label': 'Photo 1', 'image': inspection.photo_1} if inspection.photo_1 else None,
            {'label': 'Photo 2', 'image': inspection.photo_2} if inspection.photo_2 else None,
            {'label': 'Photo 3', 'image': inspection.photo_3} if inspection.photo_3 else None,
            {'label': 'Photo 4', 'image': inspection.photo_4} if inspection.photo_4 else None,
            {'label': 'Photo 5', 'image': inspection.photo_5} if inspection.photo_5 else None,
            {'label': 'Photo 6', 'image': inspection.photo_6} if inspection.photo_6 else None,
        ]

        # Remove None values from the list
        context['approved_inspectors'] = [inspector for inspector in inspectors if inspector['name'] and inspector['phone']]
        context['photos'] = [photo for photo in context['photos'] if photo is not None]

        return context
    # def get(self, request, id=None, *args, **kwargs):
    #     # GET method
    #     context = {'object': self.get_object()}
    #     #context = {'object': self.get_object()}
    #     return render(request, self.template_name, context)


class AccreditationCompletedDetailView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Appraisal
    template_name = 'monitoring/appraisals_detail.html'  # Replace with the path to your template
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Additional context or derived data
        appraisal = self.object
        context['photos'] = [
            {'label': 'Main Photo', 'image': appraisal.photo_main} if appraisal.photo_main else None,
            {'label': 'Photo 1', 'image': appraisal.photo_1} if appraisal.photo_1 else None,
            {'label': 'Photo 2', 'image': appraisal.photo_2} if appraisal.photo_2 else None,
            {'label': 'Photo 3', 'image': appraisal.photo_3} if appraisal.photo_3 else None,
            {'label': 'Photo 4', 'image': appraisal.photo_4} if appraisal.photo_4 else None,
            {'label': 'Photo 5', 'image': appraisal.photo_5} if appraisal.photo_5 else None,
            {'label': 'Photo 6', 'image': appraisal.photo_6} if appraisal.photo_6 else None,
        ]

        # Remove None values from the list
        context['photos'] = [photo for photo in context['photos'] if photo is not None]

        return context

        # context['radiographers'] = report.hospital.radiographers.all() if report.hospital else None
        # context['staff'] = report.hospital.staff.all() if report.hospital else None

        # return context


@login_required
def inspection_report(request, id):
    inspection = get_object_or_404(Inspection, pk=id)
  
    context={'inspection': inspection,        
           }
    return render(request, 'monitoring/inspections_detail.html', context)




@login_required
def approve_report(request, id):
    if request.method == 'POST':
        object = get_object_or_404(Inspection, pk=id)
        object.inspection_status = 2
        object.application_status = 6
        object.is_approved = True
        object.save()
        context = {}
        context['object'] = object
        #context['hospital'] = Hospital.objects.filter(application_no=object.application_no)
        #context['registration'] = Document.objects.filter(application_no=object.application_no)
        subject = 'Passed Facility Inspection'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [object.hospital_name.hospital_admin]   
        contact_message = get_template('monitoring/inspection_passed.txt').render(context)
        send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
        messages.success(request, ('Inspection Report Validation Successful'))    
        return render(request, 'monitoring/inspection_successful.html',context)


@login_required   
def approve_appraisal_report(request, id):
    if request.method == 'POST':
      object = get_object_or_404(Appraisal, pk=id)
      object.appraisal_status = 2
      object.application_status = 6
      object.is_approved = True
      object.save()
      context = {}
      context['object'] = object
      subject = 'Passed Facility Accreditation'
      from_email = settings.DEFAULT_FROM_EMAIL
      to_email = [object.hospital_name.hospital_admin]   
      contact_message = get_template('monitoring/accreditation_passed.txt').render(context)
      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
      messages.success(request, ('Internship Accreditation Report Validation Successful'))    
      return render(request, 'monitoring/appraisal_successful.html',context)






# @login_required
# def reject_appraisal_report(request, id):
#     if request.method == 'POST':
#       object = get_object_or_404(Appraisal, pk=id)
#       object.appraisal_status = 3
#       object.save()
#       context = {}
#       context['object'] = object
#       subject = 'Failed Accreditation Report Validation'
#       from_email = settings.DEFAULT_FROM_EMAIL
#       to_email = [object.hospital_name.hospital_admin]    
#       contact_message = get_template('monitoring/appraisal_failed.txt').render(context)
#       send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
#       messages.error(request, ('Accreditation report not approved.'))
#       return render(request, 'monitoring/inspection_failed.html',context)

# @login_required 
# def reject_application(request, id):
#     if request.method == "POST":
#         application = get_object_or_404(Payment, pk=id)
#         rejection_reason = request.POST.get("rejection_reason")

#         # Save the rejection reason to the application
#         application.vet_status = 3
#         application.is_rejected = True
#         application.rejection_reason = rejection_reason
#         application.application_status = 3
#         application.vetting_officer = request.user
#         application.save()

#         messages.error(request, "Application rejected with reason: " + rejection_reason)
#         return redirect("monitoring:rejection_details", id=application.id)



@login_required
def reject_report(request, id):
    if request.method == 'POST':
      report = get_object_or_404(Inspection, pk=id)
      rejection_reason = request.POST.get("rejection_reason")
      report.rejection_reason = rejection_reason
      report.inspection_status = 3
      report.is_rejected = True
      report.save()
      messages.error(request, "Report rejected with reason: " + rejection_reason)
      return redirect("monitoring:inspection_rejection_details", id=report.id) 





      # object = get_object_or_404(Inspection, pk=id)
      # object.inspection_status = 3
      # object.save()
      # context = {}
      # context['object'] = object
      # subject = 'Failed Inpsection Report Validation'
      # from_email = settings.DEFAULT_FROM_EMAIL
      # to_email = [object.hospital_name.hospital_admin]    
      # contact_message = get_template('monitoring/inspection_failed.txt').render(context)
      # send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
      # messages.error(request, ('Inspection failed.  Hospital will be contacted and guided on how to remedy inspection shortfalls.'))
      # return render(request, 'monitoring/inspection_failed.html',context)


@login_required
def reject_appraisal_report(request, id):
    if request.method == 'POST':
      report = get_object_or_404(Appraisal, pk=id)
      rejection_reason = request.POST.get("rejection_reason")
      report.rejection_reason = rejection_reason
      report.appraisal_status = 3
      report.is_rejected = True
      report.save()
      messages.error(request, "Application rejected with reason: " + rejection_reason)
      return redirect("monitoring:appraisal_rejection_details", id=report.id)    


def appraisal_rejection_details(request, id):
    object = get_object_or_404(Appraisal, pk=id)
    return render(request, "monitoring/appraisal_rejection_details.html", {"object": object})



def inspection_rejection_details(request, id):
    object = get_object_or_404(Inspection, pk=id)
    return render(request, "monitoring/inspection_rejection_details.html", {"object": object})

@login_required
def validate(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  context={'appraisal': appraisal,        
           }
  return render(request, 'monitoring/appraisals_detail.html', context)

@login_required
def view_appraisal_report(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  context={'appraisal': appraisal,        
           }
  return render(request, 'monitoring/appraisals_report_detail.html', context)

#class LicenseIssueListView(LoginRequiredMixin, ListView):
    #template_name = "monitoring/license_issue_list.html"
    #context_object_name = 'object'
    #queryset = Inspection.objects.all().filter(application_status=7)
    
    #def get_context_data(self, **kwargs):
        #obj = super(LicenseIssueListView, self).get_context_data(**kwargs)
        #obj['inspection'] = self.queryset.filter(application_status=7).count()
        #return obj


class LicenseIssueListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'monitoring/license_issue_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(LicenseIssueListView, self).get_context_data(**kwargs)     
        obj['inspection'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit').count()
        obj['permitr'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit').count()
        obj['appraisal'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation').count()   
        return obj   

class LicenseIssueListTable(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/license_list_table.html"
    context_object_name = 'object'  
    def get_queryset(self):
        return Inspection.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(LicenseIssueListTable, self).get_context_data(**kwargs)
        obj['issue_license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')  
        return obj   

class AccreditationIssueListTable(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/accreditation_list_table.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return Inspection.objects.all()    
    def get_context_data(self, **kwargs):
        obj = super(AccreditationIssueListTable, self).get_context_data(**kwargs)
        obj['issue_appraisal_qs'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation')         
        return obj     


class RenewalIssueListTable(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/renewal_list_table2.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return Payment.objects.all() 
    def get_context_data(self, **kwargs):
        obj = super(RenewalIssueListTable, self).get_context_data(**kwargs)
        obj['issue_renewal_qs'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')         
        return obj   

class RecordsCreateView(StaffRequiredMixin, LoginRequiredMixin, CreateView):
    template_name = 'monitoring/create_hospital_records.html'
    form_class = RecordsModelForm
    def get_success_url(self):
        return reverse('monitoring:hospital_record_details', kwargs={'id' : self.object.id})

class PermitRenewalDetails(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "monitoring/practice_permit_renewal_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)   

class LicenseDetailView1(StaffRequiredMixin, LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "monitoring/licenses_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

# class AccreditationDetailView(StaffRequiredMixin, LoginRequiredMixin, AccreditationObjectMixin, View):
#     template_name = "monitoring/accreditation_detail.html" # DetailView
#     def get(self, request, id=None, *args, **kwargs):
#         # GET method
#         context = {'object': self.get_object()}
#         return render(request, self.template_name, context)


class LicenseDetailView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Inspection
    template_name = "monitoring/licenses_detail.html" # DetailView
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inspection = self.object
        context['photos'] = [
            {'label': 'Main Photo', 'image': inspection.photo_main} if inspection.photo_main else None,
            {'label': 'Photo 1', 'image': inspection.photo_1} if inspection.photo_1 else None,
            {'label': 'Photo 2', 'image': inspection.photo_2} if inspection.photo_2 else None,
            {'label': 'Photo 3', 'image': inspection.photo_3} if inspection.photo_3 else None,
            {'label': 'Photo 4', 'image': inspection.photo_4} if inspection.photo_4 else None,
            {'label': 'Photo 5', 'image': inspection.photo_5} if inspection.photo_5 else None,
            {'label': 'Photo 6', 'image': inspection.photo_6} if inspection.photo_6 else None,
        ]
        context['photos'] = [photo for photo in context['photos'] if photo is not None]

        return context


    # def get(self, request, id=None, *args, **kwargs):
    #     # GET method
    #     context = {'object': self.get_object()}
    #     return render(request, self.template_name, context)


class AccreditationDetailView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Appraisal
    template_name = "monitoring/accreditation_detail.html"  # Replace with the path to your template
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appraisal = self.object
        context['photos'] = [
            {'label': 'Main Photo', 'image': appraisal.photo_main} if appraisal.photo_main else None,
            {'label': 'Photo 1', 'image': appraisal.photo_1} if appraisal.photo_1 else None,
            {'label': 'Photo 2', 'image': appraisal.photo_2} if appraisal.photo_2 else None,
            {'label': 'Photo 3', 'image': appraisal.photo_3} if appraisal.photo_3 else None,
            {'label': 'Photo 4', 'image': appraisal.photo_4} if appraisal.photo_4 else None,
            {'label': 'Photo 5', 'image': appraisal.photo_5} if appraisal.photo_5 else None,
            {'label': 'Photo 6', 'image': appraisal.photo_6} if appraisal.photo_6 else None,
        ]
        context['photos'] = [photo for photo in context['photos'] if photo is not None]

        return context


#class AccreditationDetailView(LoginRequiredMixin, DetailView):
    #template_name = "monitoring/accreditation_detail.html"
    #model = Appraisal
    
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #return context

class RecordsObjectMixin(object):
    model = Records
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RecordsDetailView(StaffRequiredMixin, LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "monitoring/hospitals_records_confirmation.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

class HospitalRecordsListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/hospital_records_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Records.objects.all()
    def get_context_data(self, **kwargs):
        obj = super(HospitalRecordsListView, self).get_context_data(**kwargs)
        obj['records_qs'] = Records.objects.order_by('-date_visited')
        return obj


class HospitalRecordsDetailView(StaffRequiredMixin, LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "monitoring/hospital_records_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AccreditationObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class IssueLicenseView(StaffRequiredMixin, LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_license.html'
    form_class = LicenseModelForm
    def get_success_url(self):
        return reverse("monitoring:issued_license_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.inspection.hospital_name)     
        return context
    def get_initial(self):    
        return {
            'inspection': self.kwargs["pk"],      
        }
    def get_form_kwargs(self):
        self.inspection = Inspection.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.inspection.hospital_name
        kwargs['initial']['hospital'] = self.inspection.hospital
        kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.inspection.application_no
        kwargs['initial']['schedule'] = self.inspection.schedule 
        return kwargs  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

  

class IssueRadCertPermitView(StaffRequiredMixin, LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_license.html'
    form_class = LicenseModelForm
    def get_success_url(self):
        return reverse("monitoring:issued_license_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.inspection.hospital_name)     
        return context
    def get_initial(self):    
        return {
            'inspection': self.kwargs["pk"],      
        }
    def get_form_kwargs(self):
        self.inspection = Inspection.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.inspection.hospital_name
        kwargs['initial']['hospital'] = self.inspection.hospital
        kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.inspection.application_no
        kwargs['initial']['schedule'] = self.inspection.schedule 
        return kwargs  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class IssueRadPracticePermitView(StaffRequiredMixin, LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_license.html'
    form_class = LicenseModelForm
    def get_success_url(self):
        return reverse("monitoring:rad_practice_permit_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.inspection.hospital_name)     
        return context
    def get_initial(self):    
        return {
            'inspection': self.kwargs["pk"],      
        }
    def get_form_kwargs(self):
        self.inspection = Inspection.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.inspection.hospital_name
        kwargs['initial']['hospital'] = self.inspection.hospital
        kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.inspection.application_no
        kwargs['initial']['schedule'] = self.inspection.schedule 
        return kwargs  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())



class IssueRadPracticePermitRenewal(StaffRequiredMixin, LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_practice_permit_renewal.html'
    form_class = PermitRenewalModelForm
    def get_success_url(self):
        return reverse("monitoring:rad_practice_permit_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.payment.hospital_name)     
        return context
    def get_initial(self):    
        return {
            'payment': self.kwargs["pk"],      
        }
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        #kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.payment.application_no
        #kwargs['initial']['schedule'] = self.inspection.schedule 
        return kwargs  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())




class LicenseObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class LicenseIssuedDetailView(StaffRequiredMixin, LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/license_issued2.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = LicenseModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
            subject = 'Notice of Radiography License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]
            context['form'] = form
            contact_message = get_template(
               'monitoring/license_issued.txt').render(context)
            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)


class RegPermitCertDetailView(StaffRequiredMixin, LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/license_issued2.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = LicenseModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
            subject = 'Notice of Radiography License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]
            context['form'] = form
            contact_message = get_template(
               'monitoring/license_issued.txt').render(context)
            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)


class RadPracticePermitDetailView(StaffRequiredMixin, LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/practice_permit_issued.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = LicenseModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           

            subject = 'Notice of Radiography License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'monitoring/license_issued.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)




class IssueAccreditationView(StaffRequiredMixin, LoginRequiredMixin, AccreditationObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_accreditation.html'
    form_class = AccreditationModelForm

    def get_success_url(self):
        return reverse("monitoring:issued_accreditation_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accreditation_qs'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.appraisal.hospital_name)
        return context

    def get_initial(self):
        return {
            'appraisal': self.kwargs["pk"],     
        }
    
    def get_form_kwargs(self):
        self.appraisal = Appraisal.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.appraisal.hospital_name
        kwargs['initial']['hospital'] = self.appraisal.hospital
        kwargs['initial']['payment'] = self.appraisal.payment
        kwargs['initial']['application_no'] = self.appraisal.application_no
        kwargs['initial']['schedule'] = self.appraisal.schedule
        return kwargs
       

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

    #def form_invalid(self, form):
        #form = self.get_form()

        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form 
          
        #return self.render_to_response(context)




class AccreditationIssuedDetailView(StaffRequiredMixin, LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/accreditation_issued2.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AccreditationModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
            subject = 'Notice of Radiography Internship License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'monitoring/accreditation_issued.txt').render(context)
            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)



class RadRegCerttificateListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/radiography_reg_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadRegCerttificateListView, self).get_context_data(**kwargs)
        obj['rad_cert_reg'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit').order_by('-issue_date')
        return obj    


class RadPracticePermitListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/rad_practice_permit_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadPracticePermitListView, self).get_context_data(**kwargs)
        obj['rad_practice_permit'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit').order_by('-issue_date')
        return obj  


class AccreditationCertificateListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/accreditation_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(AccreditationCertificateListView, self).get_context_data(**kwargs)
        obj['accreditation_cert'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation').order_by('-issue_date')   
        return obj  


        
#class LicenseIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = 'monitoring/license_issued.html' 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = LicenseModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form


            #subject = 'Notice of Radiography License Issuance'
            #from_email = settings.DEFAULT_FROM_EMAIL
            #to_email = [request.user.email]

            #context['form'] = form
            #contact_message = get_template(
               #'monitoring/license_issued.txt').render(context)

            #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=True)

        #return render(request, self.template_name, context)


class GenerateObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


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


class GeneratePdfView(StaffRequiredMixin, LoginRequiredMixin, GenerateObjectMixin, View):
    
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



class GenerateLicense(StaffRequiredMixin, LoginRequiredMixin, GenerateObjectMixin, View):   
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



def getPDF(request, id):
    """Returns PDF as a binary stream."""

    # Use your favourite templating language here to create the RML string.
    # The generated document might depend on the web request parameters,
    # database lookups and so on - we'll leave that up to you.
    license = get_object_or_404(License, pk=id)
    context={'license': license,      
           }
    #return render(request, 'pdf/elicense.rml', context)
    t = Template(open('pdf/elicense.rml', context).read())
    c = Context({"name": name})
    rml = t.render(c)

    buf = cStringIO.StringIO()
    rml2pdf.go(rml, outputFileName=buf)
    pdfData = buf.read()

    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response


    #rml = getRML(request)  

    #buf = StringIO()

    #rml2pdf.go(rml, outputFileName=buf)
    #buf.reset()
    #pdfData = buf.read()

    #response = HttpResponse(mimetype='application/pdf')
    #response.write(pdfData)
    #response['Content-Disposition'] = 'attachment; filename=output.pdf'
    #return response


@login_required
def download_rad_cert_reg(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=portrait(A4))
    
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

    LINE_1 = 508

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


 

@login_required
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

    passport_path = object.hospital.radiographer_in_charge_passport.path
    try:
        # Try opening it to confirm it's a valid image
        with Image.open(passport_path) as img:
            img.verify()
        p.drawImage(passport_path, 356, 556, width=108, height=114)
    except (UnidentifiedImageError, OSError):
        # Optionally, draw a placeholder or skip it
        p.setFont("Helvetica", 10)
        p.drawString(360, 600, "Invalid passport image file.")




    # p.drawImage((object.hospital.radiographer_in_charge_passport.path), 356, 556, width=108, height=114)


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


@login_required
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
    p.drawCentredString(421, 390, 'Accreditation Certificate')

    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(421, 360, 'This is to certify that')

    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(421, 320, str(object.hospital_name))

    p.setFont("Helvetica", 14, leading=None)
    p.drawCentredString(421, 300, str(object.hospital.facility_address))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 263, 'having satisfied all laid down conditions by Radiographers Registration Board of Nigeria')

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 245, 'for accreditation of hospital/centre for training of Intern Radiographers')

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
    

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='accreditation_certificate.pdf')   


PAGESIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

class PdfCreator:
    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = "%d" % (doc.page)
        canvas.drawCentredString(
            0.75 * inch,
            0.75 * inch,
            page_number_text
        )
        canvas.restoreState()
    def get_body_style(self):
        sample_style_sheet = getSampleStyleSheet()
        body_style = sample_style_sheet['BodyText']
        body_style.fontSize = 18
        return body_style
    
    def build_pdf(self):
        pdf_buffer = BytesIO()
        my_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=PAGESIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN
        )
        body_style = self.get_body_style()
        flowables = [
            Paragraph("First paragraph", body_style),
            Paragraph("Second paragraph", body_style)
        ]
        my_doc.build(
            flowables,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()
        return pdf_value


class RegisteredHospitalsListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "monitoring/registered_hospitals_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return License.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(RegisteredHospitalsListView, self).get_context_data(**kwargs)
        obj['hospitals_qs'] = License.objects.order_by('-issue_date')
        return obj
        


class RegisteredObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RegisterdHospitalsDetailView(StaffRequiredMixin, LoginRequiredMixin, RegisteredObjectMixin, View):
    template_name = "monitoring/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)






     




