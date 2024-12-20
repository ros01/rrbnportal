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

class InspectionView(LoginRequiredMixin, ScheduleObjectMixin, View):
    template_name = "zonal_offices/inspection_scheduled_details.html" 

      
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

class InspectionReportsView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/inspection_reports_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()


    def get_context_data(self, **kwargs):
        obj = super(InspectionReportsView, self).get_context_data(**kwargs)
        obj['inspection_qs'] = Inspection.objects.select_related("hospital_name")
        obj['accreditation_qs'] = Appraisal.objects.select_related("hospital_name")
        return obj


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
#def view_inspection_report(request, id):
  #inspection = get_object_or_404(Inspection, pk=id)
  
  #context={'inspection': inspection,
           
          # }
  #return render(request, 'zonal_offices/inspection_details.html', context)


#class InspectionView(LoginRequiredMixin, DetailView):
    #template_name = "zonal_offices/inspection_detail.html"
    #model = Schedule
    
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        #return context

#class InspectionReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    #template_name = "zonal_offices/inspection_report.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)


#class InspectionReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    #template_name = "zonal_offices/inspection_report.html"
    #template_name1 = "zonal_offices/inspection_report_confirmation.html"
    #def get(self, request,  *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = InspectionModelForm(instance=obj)  
            #context['object'] = obj
            #context['form'] = form

        #return render(request, self.template_name, context)


    #def post(self, request,  *args, **kwargs):
        #form = InspectionModelForm(request.POST, request.FILES)
        #if form.is_valid():
            #form.save()

        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form

           #subject = 'Notice of Facility Inspection'
           #from_email = settings.DEFAULT_FROM_EMAIL
           #to_email = [form.cleaned_data.get('email')]

           #context['form'] = form
           #contact_message = get_template(
               #'zonal_offices/inspection_report.txt').render(context)

           #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)
        #return render(request, self.template_name1, context)
        
class InspectionReportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Inspection
    template_name = 'zonal_offices/inspection_report.html'
    form_class = InspectionModelForm

    def get_success_url(self):
        return reverse("zonal_offices:inspection_complete_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice Permit')

        
        #context = {'object': self.get_object()}
        #context['payment'] = Payment.objects.get(pk=self.object)
        #context['hospital'] = Hospital.objects.get(id=self.kwargs['id'])
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'schedule': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.schedule.hospital_name
        kwargs['initial']['hospital'] = self.schedule.hospital
        kwargs['initial']['payment'] = self.schedule.payment
        kwargs['initial']['application_no'] = self.schedule.application_no
        #kwargs['initial']['hospital'] = self.payment.hospital
        
        return kwargs
      

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


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



class AccreditationReportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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

class NuclearMedicineScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class RadiotherapyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class MriScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class CtscanScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class XrayScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class FlouroscopyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class MamographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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


class DentalXrayScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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

class EchocardiographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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
        
class AngiographyScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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


class CarmScore(LoginRequiredMixin, ScheduleObjectMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
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


 
class UltrasoundScoreUpdate(UltrasoundObjectMixin, View):
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

 
class NuclearMedicineScoreUpdate(NuclearMedicineObjectMixin, View):
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

 
class RadiotherapyScoreUpdate(RadiotherapyObjectMixin, View):
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

 
class MriScoreUpdate(MriObjectMixin, View):
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

 
class CtscanScoreUpdate(CtscanObjectMixin, View):
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

 
class XrayScoreUpdate(XrayObjectMixin, View):
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

 
class FlouroscopyScoreUpdate(FlouroscopyObjectMixin, View):
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

 
class MamographyScoreUpdate(MamographyObjectMixin, View):
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

 
class DentalXrayScoreUpdate(DentalXrayObjectMixin, View):
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

 
class EchocardiographyScoreUpdate(EchocardiographyObjectMixin, View):
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

 
class AngiographyScoreUpdate(AngiographyObjectMixin, View):
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

 
class CarmScoreUpdate(CarmObjectMixin, View):
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
