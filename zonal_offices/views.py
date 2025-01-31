from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import zonaloffices_required
from accounts.models import Hospital
from hospitals.models import Schedule, Inspection, License, Records, Ultrasound, Xray, Nuclearmedicine, Radiotherapy, Mri, Ctscan, Xray, Flouroscopy, Mamography, Dentalxray, Echocardiography, Angiography, Carm, Appraisal
from django.views import View
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)

from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.generic import BSModalCreateView
from bootstrap_modal_forms.mixins import PassRequestMixin, CreateUpdateAjaxMixin
from django.contrib import messages
from . import views
from .forms import *
from monitoring.forms import *
from .models import *
from accounts.forms import *
import os
import mimetypes
from django.contrib.messages.views import SuccessMessageMixin
import io, csv
from django.contrib.auth.hashers import make_password
from django.db.models import Max, Value, IntegerField, CharField, Q, Count


class StaffRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role == 'Zonal Offices':
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(StaffRequiredMixin, self).dispatch(request,
            *args, **kwargs)



@login_required
def monitoring_dashboard(request):
    return render(request, 'monitoring/monitoring_dashboard.html')



class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)




class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "zonal_offices/zonal_offices_dashboard.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardTemplateView, self).get_context_data(*args, **kwargs)
        context["inspection"] = Schedule.objects.all()
        return context


class MyUserAccount(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'zonal_offices/my_profile.html')
        
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
        template_name = 'zonal_offices/bulk_create_hospitals.html'
        return render(request, template_name, {'form':form})
            
    def post(self, request, *args, **kwargs):
        paramFile = io.TextIOWrapper(request.FILES['hospitals_list'].file)
        portfolio1 = csv.DictReader(paramFile)
        list_of_dict = list(portfolio1)
        email_check = list_of_dict[0]["email"] == None
      

        try:
            context = {}
            if len(list_of_dict) == 0:
                messages.error(request, "No Data in List. Please populate list and try again")
                print("Number in List:",  len(list_of_dict))
                return redirect("zonal_offices:create_hospital_profile")



            elif email_check:
                messages.error(request, "No email in list. Please add email and try again")
                print("Number of emails in List:",  len(data[0]["email"]))
                return redirect("zonal_offices:create_hospital_profile")


            else:            
                for row in list_of_dict:
                    data = row['email']
                    print("Email in Data:", data)
                    userslist = User.objects.filter(email=data)
                    print("Userslist:", userslist)
                    try:
                        if userslist.exists():
                            messages.error(request, f'This User: {data} and possibly other users on this list exit already exist')
                            return redirect("zonal_offices:create_hospital_profile")
                        else:
                            for data in list_of_dict:
                                data = User.objects.create(email=row['email'], last_name=row['last_name'], first_name=row['first_name'], is_active = True, hospital = True, password = make_password('rrbnhq123%'),) 

                                objs = [
                                    Hospital(
                                        hospital_admin = User.objects.get(email=data),
                                        type = request.POST['type'],
                                        hospital_name = row['hospital_name'],
                                        phone_no = row['phone_no'],
                                    )
                                    for row in list_of_dict     
                                 ]
                                nmsg = Hospital.objects.bulk_create(objs)
                                messages.success(request, "Bulk Creation of Hospitals successful!")
                                # print("Number of emails in List:",  len(list_of_dict))
                                returnmsg = {"status_code": 200}
                                # for obj in objs:
                                #     user = obj.hospital_admin
                                return redirect("zonal_offices:create_hospital_profile")               
                    except Exception as e:
                        messages.error(request, e)

                        
        except Exception as e:
            print('Error While Importing Data: ', e)
            returnmsg = {"status_code": 500}
        return JsonResponse(returnmsg)




class HospitalsUpdatedUploadListView(StaffRequiredMixin, ListView):
    template_name = "zonal_offices/hospitals_upload_list.html"
    def get_queryset(self):
        # request = self.request
        # user = request.user
        qs = Hospital.objects.filter(application_status = 2).order_by('-date')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs 


class HospitalUploadListView(StaffRequiredMixin, ListView):
    template_name = "zonal_offices/hospitals_upload_list.html"
    def get_queryset(self):
        # request = self.request
        # user = request.user
        qs = Hospital.objects.filter(application_status = 1).order_by('-date')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs 


class NewHospitalProfileDetails(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "zonal_offices/new_hospital_profile_details.html"
    model = Hospital



class UpdateHospitalProfileDetails (StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    user_form = UserUpdateForm
    form = HospitalProfileModelForm
    template_name = "zonal_offices/update_hospital_profile_details.html"

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
            hospital_admin=self.object.hospital_admin.get_full_name,
        )

    def get_success_url(self):
        return reverse("zonal_offices_dashboard:hospitals_upload_list") 


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
            return redirect(hospital.get_zonal_absolute_url())
        else:
            messages.error(request, 'Hospital Profile Update Failed.')
            hospital = Hospital.objects.filter(hospital_admin=user).first() 
            return redirect(hospital.get_zonal_absolute_url())
        return super(UpdateHospitalProfileDetails, self).form_valid(form and user_form)





class InspectionScheduleListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/inspection_schedule_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.all()
        

    def get_context_data(self, **kwargs):
        obj = super(InspectionScheduleListView, self).get_context_data(**kwargs)
        obj['enugu_qs'] = Schedule.objects.filter(inspection_zone="Enugu", application_status=4)
        obj['abuja_qs'] = Schedule.objects.filter(inspection_zone="Abuja", application_status=4)
        obj['lagos_qs'] = Schedule.objects.filter(inspection_zone="Lagos", application_status=4)
        obj['sokoto_qs'] = Schedule.objects.filter(inspection_zone="Sokoto", application_status=4)
        obj['kano_qs'] = Schedule.objects.filter(inspection_zone="Kano", application_status=4)
        obj['ph_qs'] = Schedule.objects.filter(inspection_zone="Port Harcourt", application_status=4)
        obj['awka_qs'] = Schedule.objects.filter(inspection_zone="Awka", application_status=4)
        obj['calabar_qs'] = Schedule.objects.filter(inspection_zone="Calabar", application_status=4)
        obj['ilesha_qs'] = Schedule.objects.filter(inspection_zone="Ilesha", application_status=4)
        obj['maiduguri_qs'] = Schedule.objects.filter(inspection_zone="Maiduguri", application_status=4)
        return obj


class EnuguScheduleListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/enugu_schedule_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Enugu")
        

    def get_context_data(self, **kwargs):
        obj = super(EnuguScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Enugu", application_status=4)
        return obj


class LagosScheduleListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/lagos_schedule_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Lagos")
        

    def get_context_data(self, **kwargs):
        obj = super(LagosScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Lagos", application_status=4)
        return obj

class AbujaScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/abuja_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Abuja")


    def get_context_data(self, **kwargs):
        obj = super(AbujaScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Abuja", application_status=4)
        return obj


class PortHarcourtScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/ph_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Port Harcourt")


    def get_context_data(self, **kwargs):
        obj = super(PortHarcourtScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Port Harcourt", application_status=4)
        return obj

class AsabaScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/asaba_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Asaba")


    def get_context_data(self, **kwargs):
        obj = super(AsabaScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Asaba", application_status=4)
        return obj

class CalabarScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/calabar_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Calabar")


    def get_context_data(self, **kwargs):
        obj = super(CalabarScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Calabar", application_status=4)
        return obj
   
class KanoScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/kano_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Kano")


    def get_context_data(self, **kwargs):
        obj = super(KanoScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Kano", application_status=4)
        return obj
   

class ScheduleObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
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

class InspectionView1(LoginRequiredMixin, ScheduleObjectMixin, View):
    template_name = "zonal_offices/inspection_scheduled_details.html" 

      
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionView(StaffRequiredMixin, LoginRequiredMixin, DetailView):
    model = Schedule
    template_name = "zonal_offices/inspection_scheduled_details.html"
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


class InspectionReportsView1(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/inspection_reports_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()


    def get_context_data(self, **kwargs):
        obj = super(InspectionReportsView, self).get_context_data(**kwargs)
        obj['inspection_qs'] = Inspection.objects.select_related("hospital_name")
        obj['accreditation_qs'] = Appraisal.objects.select_related("hospital_name")
        return obj


class InspectionReportsView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/inspection_reports_list.html'

    def get_queryset(self):
        inspections = Inspection.objects.annotate(
            appraisal_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for appraisal status
        ).select_related("hospital_name").filter(vet_status=4)

        appraisals = Appraisal.objects.annotate(
            inspection_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for inspection status
        ).select_related("hospital_name").filter(vet_status=4)

        # Combine the two querysets into one
        return list(inspections) + list(appraisals)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_records'] = self.get_queryset()
        return context




class InspectionReportsRejectionsView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/inspection_reports_list.html'

    def get_queryset(self):
        inspections = Inspection.objects.annotate(
            appraisal_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for appraisal status
        ).select_related("hospital_name").filter(inspection_status=3)

        appraisals = Appraisal.objects.annotate(
            inspection_status_placeholder=Value(None, output_field=IntegerField())  # Placeholder for inspection status
        ).select_related("hospital_name").filter(appraisal_status=3)

        # Combine the two querysets into one
        return list(inspections) + list(appraisals)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combined_records'] = self.get_queryset()
        return context


class InspectionReportDetailView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_details.html" 

      
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class AccreditationReportDetailView(LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = "zonal_offices/appraisal_details.html" 

      
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)





class InspectionReportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Inspection
    template_name = 'zonal_offices/inspection_report.html'
    form_class = InspectionModelForm
    success_message = 'Inspection Report Submitted Successfully'

    def get_success_url(self):
        return reverse("zonal_offices:inspection_complete_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4,
            hospital_name=self.schedule.hospital_name,
            hospital__license_type='Radiography Practice Permit',
            application_no=self.schedule.application_no
        )

        # Add modalities and their corresponding URL names
        modalities = [
            "Ultrasound",
            "Conventional X-ray",
            "CT Scan",
            "MRI",
            "Radiotherapy",
            "Nuclear Medicine",
            "Mamography",
            "Dental X-ray",
            "Echocardiography",
            "Angiography",
            "C-Arm/O-ARM",
        ]
        context['modality_url_names'] = {
            "Ultrasound": "zonal_offices:ultrasound_score",
            "Conventional X-ray": "zonal_offices:xray_score",
            "CT Scan": "zonal_offices:ctscan_score",
            "MRI": "zonal_offices:mri_score",
            "Radiotherapy": "zonal_offices:radiotherapy_score",
            "Nuclear Medicine": "zonal_offices:nuclear_medicine_score",
            "Mamography": "zonal_offices:mamography_score",
            "Dental X-ray": "zonal_offices:dental_xray_score",
            "Echocardiography": "zonal_offices:echocardiography_score",
            "Angiography": "zonal_offices:angiography_score",
            "C-Arm/O-ARM": "zonal_offices:carm_score",
        }
        context['photo_range'] = range(1, 7) 
        context['schedule_qs'] = schedule_qs
        context['modalities'] = modalities
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }

    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['hospital'] = self.schedule.hospital
        kwargs['initial']['payment'] = self.schedule.payment
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_valid(self, form):
        if Inspection.objects.filter(schedule=self.schedule).exists():
            # Add message to context instead of relying solely on messages framework
            context = self.get_context_data()
            context['error_message'] = "An inspection report for this schedule already exists."
            return self.render_to_response(context)
        return super().form_valid(form)
    

    def form_invalid(self, form):
        # Retrieve all form errors
        error_messages = form.errors.as_json()  # Get errors in JSON format for better debugging
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]

        non_field_errors = form.non_field_errors()
        if non_field_errors:
            messages.error(self.request, f"{', '.join(non_field_errors)}")

        
        return self.render_to_response(self.get_context_data(form=form))





class InspectionCompleteDetailView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = 'zonal_offices/inspection_report_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = InspectionModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
            subject = 'Hospital/Centre Inspection Report'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'zonal_offices/inspection_report.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)



class AccreditationReportView1(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Appraisal
    template_name = 'zonal_offices/accreditation_report_form.html'
    form_class = InternshipModelForm

    def get_success_url(self):
        return reverse("zonal_offices:accreditation_complete_details", kwargs={"id": self.object.id})


    #def get(self, *args, **kwargs):
        #hospital_name = get_object_or_404(Schedule, pk=kwargs.get('pk'))

        #return super().get(self)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['schedule_qss'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship', application_no=self.schedule.application_no)
        context['schedule_qsss'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship', application_no=self.schedule.application_no)
        #context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal')
        context['schedule_qssr'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship', application_no=self.schedule.application_no)
        context['schedule_qgssr'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship', application_no=self.schedule.application_no)
        return context

    def get_initial(self, *args, **kwargs):
        # You could even get the Book model using Book.objects.get here!
        
        return {
            'schedule': self.kwargs["pk"],
            #'hospital_name':hospital_name,
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['hospital'] = self.schedule.hospital
        kwargs['initial']['payment'] = self.schedule.payment
        kwargs['initial']['application_no'] = self.schedule.application_no
      
        
        return kwargs

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())
      
class AccreditationReportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Appraisal
    template_name = 'zonal_offices/accreditation_report_form.html'
    form_class = InternshipModelForm
    success_message = "Accreditation report created successfully."

    def get_success_url(self):
        return reverse("zonal_offices:accreditation_complete_details", kwargs={"id": self.object.id})

    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['hospital'] = self.schedule.hospital
        kwargs['initial']['payment'] = self.schedule.payment
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common_filters = {
            'application_status': 4,
            'hospital_name': self.schedule.hospital_name,
            'application_no': self.schedule.application_no,
            'hospital__license_type': 'Internship Accreditation'
        }
        context['schedule_qss'] = Schedule.objects.filter(
            **common_filters, hospital__application_type='New Registration - Government Hospital Internship'
        )
        context['schedule_qsss'] = Schedule.objects.filter(
            **common_filters, hospital__application_type='New Registration - Private Hospital Internship'
        )
        context['schedule_qssr'] = Schedule.objects.filter(
            **common_filters, hospital__application_type='Renewal - Private Hospital Internship'
        )
        context['schedule_qgssr'] = Schedule.objects.filter(
            **common_filters, hospital__application_type='Renewal - Government Hospital Internship'
        )
        return context

    def get_initial(self, *args, **kwargs):
        return {'schedule': self.kwargs["pk"]}

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())
        

class AccreditationReportUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Appraisal
    template_name = 'zonal_offices/accreditation_report_update_form.html'
    form_class = InternshipModelForm
    success_message = "Accreditation report updated successfully."

    def get_object(self):
        # Retrieves the Appraisal object using the `id` from the URL.
        return get_object_or_404(Appraisal, id=self.kwargs['id'])

    def form_valid(self, form):
        # Automatically set `appraisal_status` to 1 before saving.
        form.instance.appraisal_status = 1
        return super().form_valid(form)

    def get_success_url(self):
        # Redirects to the detailed view of the updated Appraisal.
        return reverse("zonal_offices:accreditation_complete_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        # Add custom context data if needed.
        context = super().get_context_data(**kwargs)
        context['custom_message'] = "Edit the Accreditation Report details below:"
        return context

    def form_invalid(self, form):
        # Handles invalid form submission by re-rendering the form with errors.
        return self.render_to_response(self.get_context_data())

class InspectionReportUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Inspection
    template_name = "zonal_offices/inspection_report_update.html"
    form_class = InspectionModelForm
    success_message = "Inspection Report updated successfully!"

    def get_object(self, queryset=None):
        # Get the inspection object by its primary key
        return get_object_or_404(Inspection, pk=self.kwargs["pk"])

    def get_success_url(self):
        # Redirect to the details view after a successful update
        return reverse("zonal_offices:inspection_complete_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inspection = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=inspection.schedule.pk)
        try:
            ultrasound = Ultrasound.objects.get(schedule=inspection.schedule)
        except Ultrasound.DoesNotExist:
            ultrasound = None
        
        try:
            nuclear_medicine = Nuclearmedicine.objects.get(schedule=inspection.schedule)
        except Nuclearmedicine.DoesNotExist:
            nuclear_medicine = None

        try:
            radiotherapy = Radiotherapy.objects.get(schedule=inspection.schedule)
        except Radiotherapy.DoesNotExist:
            radiotherapy = None

        try:
            mri = Mri.objects.get(schedule=inspection.schedule)
        except Mri.DoesNotExist:
            mri = None

        try:
            ctscan = Ctscan.objects.get(schedule=inspection.schedule)
        except Ctscan.DoesNotExist:
            ctscan = None

        try:
            xray = Xray.objects.get(schedule=inspection.schedule)
        except Xray.DoesNotExist:
            xray = None

        try:
            flouroscopy = Flouroscopy.objects.get(schedule=inspection.schedule)
        except Flouroscopy.DoesNotExist:
            flouroscopy = None

        try:
            mamography = Mamography.objects.get(schedule=inspection.schedule)
        except Mamography.DoesNotExist:
            mamography = None

        try:
            echocardiography = Echocardiography.objects.get(schedule=inspection.schedule)
        except Echocardiography.DoesNotExist:
            echocardiography = None

        try:
            dental_xray = Dentalxray.objects.get(schedule=inspection.schedule)
        except Dentalxray.DoesNotExist:
            dental_xray = None

        try:
            angiography = Angiography.objects.get(schedule=inspection.schedule)
        except Angiography.DoesNotExist:
            angiography = None

        try:
            carm = Carm.objects.get(schedule=inspection.schedule)
        except Carm.DoesNotExist:
            carm = None
        # Adding context for modalities and other data
        context["schedule_qs"] = schedule_qs
        context["modalities"] = [
            "Ultrasound",
            "Conventional X-ray",
            "CT Scan",
            "MRI",
            "Radiotherapy",
            "Nuclear Medicine",
            "Mamography",
            "Dental X-ray",
            "Echocardiography",
            "Angiography",
            "C-Arm/O-ARM",
        ]
        context["modality_url_names"] = {
            "Ultrasound": reverse(
                "zonal_offices:ultrasound_update", kwargs={"id": ultrasound.id}
            ) if ultrasound else None,

            "Conventional X-ray": reverse(
                "zonal_offices:xray_update", kwargs={"id": xray.id}
            ) if xray else None,


            "CT Scan": reverse(
                "zonal_offices:ctscan_update", kwargs={"id": ctscan.id}
            ) if ctscan else None,


            "MRI": reverse(
                "zonal_offices:mri_update", kwargs={"id": mri.id}
            ) if mri else None,

            "Radiotherapy": reverse(
                "zonal_offices:radiotherapy_update", kwargs={"id": radiotherapy.id}
            ) if radiotherapy else None,

            "Nuclear Medicine": reverse(
                "zonal_offices:nuclear_medicine_update", kwargs={"id": nuclear_medicine.id}
            ) if nuclear_medicine else None,

            "Mamography": reverse(
                "zonal_offices:mamography_update", kwargs={"id": mamography.id}
            ) if mamography else None,

            "Dental X-ray": reverse(
                "zonal_offices:dental_xray_update", kwargs={"id": dental_xray.id}
            ) if dental_xray else None,

            "Echocardiography": reverse(
                "zonal_offices:echocardiography_update", kwargs={"id": echocardiography.id}
            ) if echocardiography else None,

            "Angiography": reverse(
                "zonal_offices:angiography_update", kwargs={"id": angiography.id}
            ) if angiography else None,

            "C-Arm/O-ARM": reverse(
                "zonal_offices:carm_update", kwargs={"id": carm.id}
            ) if carm else None,
            
            # "Ultrasound": "zonal_offices:ultrasound_update",
            # "Conventional X-ray": "zonal_offices:xray_update",
            # "CT Scan": "zonal_offices:ctscan_update",
            # "MRI": "zonal_offices:mri_update",
            # "Radiotherapy": "zonal_offices:radiotherapy_update",
            # "Nuclear Medicine": "zonal_offices:nuclear_medicine_update",
            # "Mammography": "zonal_offices:mammography_update",
            # "Dental X-ray": "zonal_offices:dental_xray_update",
            # "Echocardiography": "zonal_offices:echocardiography_update",
            # "Angiography": "zonal_offices:angiography_update",
            # "C-Arm/O-ARM": "zonal_offices:carm_update",
        }

        return context


    def form_valid(self, form):
        # Automatically set `appraisal_status` to 1 before saving.
        form.instance.inspection_status = 1
        return super().form_valid(form)

    def form_invalid(self, form):
        # Display detailed error messages
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        messages.error(self.request, "There was an error updating the form. Please review the details.")
        return self.render_to_response(self.get_context_data(form=form))

class InspectionReportUpdateViewx(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Inspection
    template_name = 'zonal_offices/inspection_report_update_form.html'
    form_class = InspectionModelForm
    success_message = "Inspection report updated successfully."

    def get_object(self):
        # Retrieves the Appraisal object using the `id` from the URL.
        return get_object_or_404(Inspection, id=self.kwargs['id'])

    def form_valid(self, form):
        # Automatically set `appraisal_status` to 1 before saving.
        form.instance.inspection_status = 1
        return super().form_valid(form)

    def get_success_url(self):
        # Redirects to the detailed view of the updated Appraisal.
        return reverse("zonal_offices:inspection_complete_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        # Add custom context data if needed.
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.hospital_name, hospital__license_type = 'Radiography Practice Permit')
        context['custom_message'] = "Edit the Inspection Report details below:"
        return context

    def form_invalid(self, form):
        # Handles invalid form submission by re-rendering the form with errors.
        return self.render_to_response(self.get_context_data())


    
class AccreditationCompleteDetailView(LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = 'zonal_offices/accreditation_report_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AccreditationModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
            subject = 'Hospital/Centre Accreditation Report'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'zonal_offices/accreditation_report.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=True)

        return render(request, self.template_name, context)



class UltrasoundScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/ultrasound_score2.html'
    form_class = UltrasoundModelForm
    success_message = 'Ultrasound Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        ultrasound = Ultrasound.objects.filter(schedule=self.schedule).first()
        if ultrasound:
            context["ultrasound"] = ultrasound
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class UltrasoundScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Ultrasound
    template_name = "zonal_offices/ultrasound_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = UltrasoundModelForm
    success_message = "Ultrasound details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Ultrasound, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ultrasound = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=ultrasound.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["ultrasound"] = ultrasound
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class NuclearMedicineScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/nuclear_medicine_score.html'
    form_class = NuclearMedicineModelForm
    success_message = 'Nuclear Medicine Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        nuclear_medicine = Nuclearmedicine.objects.filter(schedule=self.schedule).first()
        if nuclear_medicine:
            context["nuclear_medicine"] = nuclear_medicine
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class NuclearMedicineScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Nuclearmedicine
    template_name = "zonal_offices/nuclearmedicine_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = NuclearMedicineModelForm
    success_message = "Nuclearmedicine details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Nuclearmedicine, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nuclear_medicine = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=nuclear_medicine.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["nuclear_medicine"] = nuclear_medicine
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class RadiotherapyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/radiotherapy_score.html'
    form_class = RadiotherapyModelForm
    success_message = 'Radiotherapy Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        radiotherapy = Radiotherapy.objects.filter(schedule=self.schedule).first()
        if radiotherapy:
            context["radiotherapy"] = radiotherapy
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class RadiotherapyScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Radiotherapy
    template_name = "zonal_offices/radiotherapy_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = RadiotherapyModelForm
    success_message = "Radiotherapy details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Radiotherapy, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        radiotherapy = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=radiotherapy.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["radiotherapy"] = radiotherapy
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class MriScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/mri_score.html'
    form_class = MriModelForm
    success_message = 'MRI Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        mri = Mri.objects.filter(schedule=self.schedule).first()
        if mri:
            context["mri"] = mri
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class MriScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Mri
    template_name = "zonal_offices/mri_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = MriModelForm
    success_message = "MRI details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Mri, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mri = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=mri.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["mri"] = mri
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class CtscanScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/ctscan_score.html'
    form_class = CtscanModelForm
    success_message = 'CT Scan Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        ctscan = Ctscan.objects.filter(schedule=self.schedule).first()
        if ctscan:
            context["ctscan"] = ctscan
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class CtscanScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Ctscan
    template_name = "zonal_offices/ctscan_score_update.html"  
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = CtscanModelForm
    success_message = "Ctscan details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Ctscan, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ctscan = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=ctscan.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["ctscan"] = ctscan
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))

class XrayScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/xray_score.html'
    form_class = XrayModelForm
    success_message = 'X-ray Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        xray = Xray.objects.filter(schedule=self.schedule).first()
        if xray:
            context["xray"] = xray
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class XrayScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Xray
    template_name = "zonal_offices/xray_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = XrayModelForm
    success_message = "Xray details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Xray, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        xray = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=xray.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["xray"] = xray
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class FlouroscopyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/flouroscopy_score.html'
    form_class = FlouroscopyModelForm
    success_message = 'Flouroscopy Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        flouroscopy = Flouroscopy.objects.filter(schedule=self.schedule).first()
        if flouroscopy:
            context["flouroscopy"] = flouroscopy
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class FlouroscopyScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Flouroscopy
    template_name = "zonal_offices/flouroscopy_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = FlouroscopyModelForm
    success_message = "Flouroscopy details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Flouroscopy, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flouroscopy = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=flouroscopy.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["flouroscopy"] = flouroscopy
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class MamographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/mamography_score.html'
    form_class = MamographyModelForm
    success_message = 'Mamography Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        mamography = Mamography.objects.filter(schedule=self.schedule).first()
        if mamography:
            context["mamography"] = mamography
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class MamographyScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Mamography
    template_name = "zonal_offices/mamography_score_update.html"  
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = MamographyModelForm
    success_message = "Mamography details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Mamography, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mamography = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=mamography.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["mamography"] = mamography
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))

class DentalXrayScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/dental_xray_score.html'
    form_class = DentalXrayModelForm
    success_message = 'Dental X-ray Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        dental_xray = Dentalxray.objects.filter(schedule=self.schedule).first()
        if dental_xray:
            context["dental_xray"] = dental_xray
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class DentalXrayScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Dentalxray
    template_name = "zonal_offices/dental_xray_score_update.html"  
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = DentalXrayModelForm
    success_message = "Dentalxray details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Dentalxray, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dental_xray = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=dental_xray.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["dental_xray"] = dental_xray
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class EchocardiographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/echocardiography_score.html'
    form_class = EchocardiographyModelForm
    success_message = 'Echocardiography Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        echocardiography = Echocardiography.objects.filter(schedule=self.schedule).first()
        if echocardiography:
            context["echocardiography"] = echocardiography
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class EchocardiographyScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Echocardiography
    template_name = "zonal_offices/echocardiography_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = EchocardiographyModelForm
    success_message = "Echocardiography details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Echocardiography, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        echocardiography = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=echocardiography.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["echocardiography"] = echocardiography
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class AngiographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/angiography_score.html'
    form_class = AngiographyModelForm
    success_message = 'Angiography Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        angiography = Angiography.objects.filter(schedule=self.schedule).first()
        if angiography:
            context["angiography"] = angiography
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class AngiographyScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Angiography
    template_name = "zonal_offices/angiography_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = AngiographyModelForm
    success_message = "Angiography details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Angiography, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        angiography = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=angiography.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["angiography"] = angiography
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


class CarmScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/carm_score.html'
    form_class = CarmModelForm
    success_message = 'C-Arm Score Entered Successfully'
    
    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_qs = Schedule.objects.select_related("hospital_name").filter(
            application_status=4, hospital_name=self.schedule.hospital_name
        )
        context['schedule_qs'] = schedule_qs
        
        # Ensure ultrasound object exists
        carm = Carm.objects.filter(schedule=self.schedule).first()
        if carm:
            context["carm"] = carm
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))



class CarmScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
    model = Carm
    template_name = "zonal_offices/carm_score_update.html" 
    # template_name = "zonal_offices/ultrasound_update.html"
    form_class = CarmModelForm
    success_message = "Carm details updated successfully!"

    def get_object(self, queryset=None):
        # Get the ultrasound object based on its ID
        return get_object_or_404(Carm, id=self.kwargs["id"])

    def get_success_url(self):
        if hasattr(self.object, 'schedule') and self.object.schedule:
            try:
                # Fetch the related Inspection object
                inspection = Inspection.objects.get(schedule=self.object.schedule)
                return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
            except Inspection.DoesNotExist:
                messages.error(self.request, "Inspection report not found for this schedule.")
                return reverse("zonal_offices:dashboard")
        else:
            messages.error(self.request, "Schedule not found. Please try again.")
            return reverse("zonal_offices:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass request to form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carm = self.get_object()
        schedule_qs = Schedule.objects.filter(pk=carm.schedule.pk)

        context["schedule_qs"] = schedule_qs
        context["carm"] = carm
        return context

    def form_invalid(self, form):
        # Show error messages if the form submission fails
        messages.error(self.request, "There was an error updating the form. Please check the details.")
        error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        for error in error_list:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))


# class UltrasoundScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
#     template_name = 'zonal_offices/ultrasound_score2.html'
#     form_class = UltrasoundModelForm
#     success_message = 'Ultrasound Score Entered Successfully'
    
#     def get_success_url(self):
#         if hasattr(self.object, 'schedule') and self.object.schedule:
#             return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
#         else:
#             messages.error(self.request, "Schedule not found. Please try again.")
#             return reverse("zonal_offices:dashboard")  # Fallback in case schedule is missing
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         schedule_qs = Schedule.objects.select_related("hospital_name").filter(
#             application_status=4, hospital_name=self.schedule.hospital_name
#         )
#         context['schedule_qs'] = schedule_qs
        
#         # Ensure ultrasound object exists
#         ultrasound = Ultrasound.objects.filter(schedule=self.schedule).first()
#         if ultrasound:
#             context["ultrasound"] = ultrasound
#         return context

#     def get_initial(self):
#         return {
#             'schedule': self.kwargs["pk"],
#         }
    
#     def get_form_kwargs(self):
#         self.schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
#         kwargs = super().get_form_kwargs()
#         kwargs['initial']['hospital_name'] = self.schedule.hospital_name
#         kwargs['initial']['application_no'] = self.schedule.application_no
#         return kwargs

#     def form_invalid(self, form):
#         messages.error(self.request, "There was an error submitting the form. Please check the details.")
#         error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
#         for error in error_list:
#             messages.error(self.request, error)
#         return self.render_to_response(self.get_context_data(form=form))



# class UltrasoundScoreUpdate(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, UpdateView):
#     model = Ultrasound
#     template_name = "zonal_offices/ultrasound_score_update.html" 
#     # template_name = "zonal_offices/ultrasound_update.html"
#     form_class = UltrasoundModelForm
#     success_message = "Ultrasound details updated successfully!"

#     def get_object(self, queryset=None):
#         # Get the ultrasound object based on its ID
#         return get_object_or_404(Ultrasound, id=self.kwargs["id"])

#     def get_success_url(self):
#         if hasattr(self.object, 'schedule') and self.object.schedule:
#             try:
#                 # Fetch the related Inspection object
#                 inspection = Inspection.objects.get(schedule=self.object.schedule)
#                 return reverse("zonal_offices:inspection_report_update", kwargs={"pk": inspection.pk})
#             except Inspection.DoesNotExist:
#                 messages.error(self.request, "Inspection report not found for this schedule.")
#                 return reverse("zonal_offices:dashboard")
#         else:
#             messages.error(self.request, "Schedule not found. Please try again.")
#             return reverse("zonal_offices:dashboard")

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["request"] = self.request  # Pass request to form
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         ultrasound = self.get_object()
#         schedule_qs = Schedule.objects.filter(pk=ultrasound.schedule.pk)

#         context["schedule_qs"] = schedule_qs
#         context["ultrasound"] = ultrasound
#         return context

#     def form_invalid(self, form):
#         # Show error messages if the form submission fails
#         messages.error(self.request, "There was an error updating the form. Please check the details.")
#         error_list = [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
#         for error in error_list:
#             messages.error(self.request, error)
#         return self.render_to_response(self.get_context_data(form=form))


class UltrasoundScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/ultrasound_score2.html'
    form_class = UltrasoundModelForm
    success_message = 'Ultrasound Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class NuclearMedicineScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/nuclear_medicine_score.html'
    form_class = NuclearMedicineModelForm
    success_message = 'Nuclear Medicine Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    #def form_invalid(self, form):
        #form = self.get_form()
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form 
        #return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class RadiotherapyScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/radiotherapy_score.html'
    form_class = RadiotherapyModelForm
    success_message = 'Radiotherapy Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class MriScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/mri_score.html'
    form_class = MriModelForm
    success_message = 'MRI Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class CtscanScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/ctscan_score.html'
    form_class = CtscanModelForm
    success_message = 'CT Scan Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class XrayScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/xray_score.html'
    form_class = XrayModelForm
    success_message = 'X-ray Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class FlouroscopyScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/flouroscopy_score.html'
    form_class = FlouroscopyModelForm
    success_message = 'Flouroscopy Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class MamographyScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/mamography_score.html'
    form_class = MamographyModelForm
    success_message = 'Mamography Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class DentalXrayScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/dental_xray_score.html'
    form_class = DentalXrayModelForm
    success_message = 'Dental X-ray Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class EchocardiographyScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/echocardiography_score.html'
    form_class = EchocardiographyModelForm
    success_message = 'Echocardiography Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())
        
class AngiographyScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/angiography_score.html'
    form_class = AngiographyModelForm
    success_message = 'Angiography Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class CarmScore1(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    template_name = 'zonal_offices/carm_score.html'
    form_class = CarmModelForm
    success_message = 'C-Arm Score Entered Successfully'
     
    def get_success_url(self):
        return reverse("zonal_offices:inspection_report", kwargs={"pk": self.object.schedule.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name)      
        return context

    def get_initial(self):
        return {
            'schedule': self.kwargs["pk"],
        }
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['application_no'] = self.schedule.application_no
        return kwargs
      
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

#class UltrasoundScore(BSModalCreateView):
    #template_name = 'zonal_offices/ultrasound_score.html'
    #form_class = UltrasoundModelForm
    #success_message = 'Ultrasound Score Entered Successfully.'
    #success_url = reverse_lazy('class_book_list')

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})
class UltrasoundObjectMixin(object):
    model = Ultrasound
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

#class UltrasoundScoreDetail(UltrasoundObjectMixin, View):
    #template_name = "zonal_offices/ultrasound_score_details.html"

    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)


class UltrasoundScoreDetail(LoginRequiredMixin, DetailView):
    template_name = "zonal_offices/ultrasound_score_details.html"
    model = Ultrasound
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


 
class UltrasoundScoreUpdate1(UltrasoundObjectMixin, View):
    template_name = "zonal_offices/ultrasound_score_update.html" 
    template_name1 = "zonal_offices/ultrasound_score_details.html" 
    success_message = 'Ultrasound Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = UltrasoundModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = UltrasoundModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)

#class NuclearMedicineScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/nuclear_medicine_score.html'
    #form_class = NuclearMedicineModelForm
    #success_message = 'Nuclear Medicine Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})
        

class NuclearMedicineObjectMixin(object):
    model = Nuclearmedicine
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class NuclearMedicineScoreDetail(NuclearMedicineObjectMixin, View):
    template_name = "zonal_offices/nuclear_medicine_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class NuclearMedicineScoreUpdate1(NuclearMedicineObjectMixin, View):
    template_name = "zonal_offices/nuclearmedicine_score_update.html" 
    template_name1 = "zonal_offices/nuclear_medicine_score_details.html" 
    
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = NuclearMedicineModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = NuclearMedicineModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        messages.success(request, ('Nuclear Medicine Score Updated Successfully'))
        return render(request, self.template_name1, context)

#class RadiotherapyScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/radiotherapy_score.html'
    #form_class = RadiotherapyModelForm
    #success_message = 'Radiotherapy Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})
        
class RadiotherapyObjectMixin(object):
    model = Radiotherapy
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class RadiotherapyScoreDetail(RadiotherapyObjectMixin, View):
    template_name = "zonal_offices/radiotherapy_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class RadiotherapyScoreUpdate1(RadiotherapyObjectMixin, View):
    template_name = "zonal_offices/radiotherapy_score_update.html" 
    template_name1 = "zonal_offices/radiotherapy_score_details.html" 
    success_message = 'Radiotherapy Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = RadiotherapyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = RadiotherapyModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)



#class MriScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/mri_score.html'
    #form_class = MriModelForm
    #success_message = 'MRI Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})        

class MriObjectMixin(object):
    model = Mri
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class MriScoreDetail(MriObjectMixin, View):
    template_name = "zonal_offices/mri_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class MriScoreUpdate1(MriObjectMixin, View):
    template_name = "zonal_offices/mri_score_update.html" 
    template_name1 = "zonal_offices/mri_score_details.html" 
    success_message = 'Mri Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MriModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MriModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)




#class CtscanScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/ctscan_score.html'
    #form_class = CtscanModelForm
    #success_message = 'CT Scan Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})


class CtscanObjectMixin(object):
    model = Ctscan
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class CtscanScoreDetail(CtscanObjectMixin, View):
    template_name = "zonal_offices/ctscan_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class CtscanScoreUpdate1(CtscanObjectMixin, View):
    template_name = "zonal_offices/ctscan_score_update.html" 
    template_name1 = "zonal_offices/ctscan_score_details.html" 
    success_message = 'Ctscan Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CtscanModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CtscanModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)


#class XrayScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/xray_score.html'
    #form_class = XrayModelForm
    #success_message = 'Conventional X-ray Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})
        #return reverse("zonal_offices:xray_detail", kwargs={"id": self.object.practice_manager.xray.id})

class XrayObjectMixin(object):
    model = Xray
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class XrayScoreDetail(XrayObjectMixin, View):
    template_name = "zonal_offices/xray_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class XrayScoreUpdate1(XrayObjectMixin, View):
    template_name = "zonal_offices/xray_score_update.html" 
    template_name1 = "zonal_offices/xray_score_details.html" 
    success_message = 'Xray Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = XrayModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = XrayModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)



#class FluoroscopyScore(LoginRequiredMixin, BSModalCreateView):
    #template_name = 'zonal_offices/fluoroscopy_score.html'
    #form_class = FluoroscopyModelForm
    #success_message = 'Conventional X-ray with Fluoroscopy Score Entered Successfully.'

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})


class FlouroscopyObjectMixin(object):
    model = Flouroscopy
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class FlouroscopyScoreDetail(FlouroscopyObjectMixin, View):
    template_name = "zonal_offices/flouroscopy_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class FlouroscopyScoreUpdate1(FlouroscopyObjectMixin, View):
    template_name = "zonal_offices/flouroscopy_score_update.html" 
    template_name1 = "zonal_offices/flouroscopy_score_details.html" 
    success_message = 'Flouroscopy Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = FlouroscopyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = FlouroscopyModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)
        
class MamographyObjectMixin(object):
    model = Mamography
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class MamographyScoreDetail(MamographyObjectMixin, View):
    template_name = "zonal_offices/mamography_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class MamographyScoreUpdate1(MamographyObjectMixin, View):
    template_name = "zonal_offices/mamography_score_update.html" 
    template_name1 = "zonal_offices/mamography_score_details.html" 
    success_message = 'Mamography Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MamographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MamographyModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)
        
class DentalXrayObjectMixin(object):
    model = Dentalxray
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class DentalXrayScoreDetail(DentalXrayObjectMixin, View):
    template_name = "zonal_offices/dental_xray_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class DentalXrayScoreUpdate1(DentalXrayObjectMixin, View):
    template_name = "zonal_offices/dental_xray_score_update.html" 
    template_name1 = "zonal_offices/dental_xray_score_details.html" 
    success_message = 'Dental X-ray Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = DentalXrayModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = DentalXrayModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)        

class EchocardiographyObjectMixin(object):
    model = Echocardiography
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class EchocardiographyScoreDetail(EchocardiographyObjectMixin, View):
    template_name = "zonal_offices/echocardiography_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class EchocardiographyScoreUpdate1(EchocardiographyObjectMixin, View):
    template_name = "zonal_offices/echocardiography_score_update.html" 
    template_name1 = "zonal_offices/echocardiography_score_details.html" 
    success_message = 'Echocardiography Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = EchocardiographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = EchocardiographyModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)


        
class AngiographyObjectMixin(object):
    model = Angiography
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class AngiographyScoreDetail(AngiographyObjectMixin, View):
    template_name = "zonal_offices/angiography_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class AngiographyScoreUpdate1(AngiographyObjectMixin, View):
    template_name = "zonal_offices/angiography_score_update.html" 
    template_name1 = "zonal_offices/angiography_score_details.html" 
    success_message = 'Angiography Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AngiographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AngiographyModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)

        
class CarmObjectMixin(object):
    model = Carm
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class CarmScoreDetail(CarmObjectMixin, View):
    template_name = "zonal_offices/carm_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
class CarmScoreUpdate1(CarmObjectMixin, View):
    template_name = "zonal_offices/carm_score_update.html" 
    template_name1 = "zonal_offices/carm_score_details.html" 
    success_message = 'C-Arm Score Updated Successfully.'

    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CarmModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CarmModelForm(request.POST or None, instance=obj)
            if form.is_valid():
                form.save()
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name1, context)


    
class RecordsCreate(LoginRequiredMixin, CreateView):
    template_name = 'zonal_offices/create_hospital_records.html'

    form_class = RecordsModelForm

    def get_success_url(self):
        return reverse('zonal_offices:hospital_record_details', kwargs={'id' : self.object.id})

   

class RecordsObjectMixin(object):
    model = Records
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RecordsDetail(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "zonal_offices/hospitals_records_confirmation.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class HospitalRecordsList(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/hospital_records_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Records.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(HospitalRecordsList, self).get_context_data(**kwargs)
        obj['records_qs'] = Records.objects.order_by('-date_visited')
        return obj
        



class HospitalRecordsDetail(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "zonal_offices/hospital_records_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)







class RegisteredHospitalsListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/registered_hospitals_list.html"
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


class RegisterdHospitalsDetailView(LoginRequiredMixin, RegisteredObjectMixin, View):
    template_name = "zonal_offices/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



@login_required
def offices(request):
  return render(request, 'zonal_offices/rrbn_offices.html')
