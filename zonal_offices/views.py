from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import zonaloffices_required
from hospitals.models import Schedule, Inspection, License, Records, Ultrasound, Xray, Nuclearmedicine, Radiotherapy, Mri, Ctscan, Xray, Flouroscopy, Mamography, Dentalxray, Echocardiography, Angiography, Carm
from .forms import InspectionModelForm, RecordsModelForm, AccreditationModelForm, UltrasoundModelForm, XrayModelForm, FlouroscopyModelForm, CtscanModelForm, MriModelForm, NuclearMedicineModelForm, RadiotherapyModelForm,  MamographyModelForm, DentalXrayModelForm, EchocardiographyModelForm, AngiographyModelForm, CarmModelForm
from django.views import View
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.generic import BSModalCreateView



class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)




class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "zonal_offices/zonal_offices_dashboard.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardTemplateView, self).get_context_data(*args, **kwargs)
        context["inspection"] = Schedule.objects.all()
        return context


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
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.filter(inspection_zone="Abuja")


    def get_context_data(self, **kwargs):
        obj = super(AbujaScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Abuja", application_status=4)
        return obj
        

class InspectionObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_detail.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


#class InspectionReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    #template_name = "zonal_offices/inspection_report.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)


class InspectionReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_report.html"
    template_name1 = "zonal_offices/inspection_report_confirmation.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = InspectionModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)


    def post(self, request,  *args, **kwargs):
        form = InspectionModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Notice of Facility Inspection'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'zonal_offices/inspection_report.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        return render(request, self.template_name1, context)
        
        
#class UltrasoundScore(BSModalCreateView):
    #template_name = 'zonal_offices/ultrasound_score.html'
    #form_class = UltrasoundModelForm
    #success_message = 'Ultrasound Score Entered Successfully.'
    #success_url = reverse_lazy('class_book_list')

    #def get_success_url(self):
        #return reverse("zonal_offices:inspection_report", kwargs={"id": self.object.practice_manager.schedule.id})


class UltrasoundScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/ultrasound_score.html'
    template_name1 = 'zonal_offices/ultrasound_score_details.html'
    success_message = 'Ultrasound Score Entered Successfully'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = UltrasoundModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = UltrasoundModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = UltrasoundModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

class UltrasoundObjectMixin(object):
    model = Ultrasound
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class UltrasoundScoreDetail(UltrasoundObjectMixin, View):
    template_name = "zonal_offices/ultrasound_score_details.html"

    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

 
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

class NuclearMedicineScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/nuclear_medicine_score.html'
    template_name1 = 'zonal_offices/nuclear_medicine_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = NuclearMedicineModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = NuclearMedicineModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = NuclearMedicineModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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


class RadiotherapyScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/radiotherapy_score.html'
    template_name1 = 'zonal_offices/radiotherapy_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = RadiotherapyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = RadiotherapyModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = RadiotherapyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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

class MriScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/mri_score.html'
    template_name1 = 'zonal_offices/mri_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MriModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = MriModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MriModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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


class CtscanScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/ctscan_score.html'
    template_name1 = 'zonal_offices/ctscan_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CtscanModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = CtscanModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CtscanModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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


class XrayScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/xray_score.html'
    template_name1 = 'zonal_offices/xray_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = XrayModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = XrayModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = XrayModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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



class FlouroscopyScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/flouroscopy_score.html'
    template_name1 = 'zonal_offices/flouroscopy_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = FlouroscopyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = FlouroscopyModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = FlouroscopyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name1, context)
        

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



class MamographyScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/mamography_score.html'
    template_name1 = 'zonal_offices/mamography_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MamographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = MamographyModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = MamographyModelForm(instance=obj)
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


class DentalXrayScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/dental_xray_score.html'
    template_name1 = 'zonal_offices/dental_xray_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = DentalXrayModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = DentalXrayModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = DentalXrayModelForm(instance=obj)
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


class EchocardiographyScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/echocardiography_score.html'
    template_name1 = 'zonal_offices/echocardiography_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = EchocardiographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = EchocardiographyModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = EchocardiographyModelForm(instance=obj)
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



class AngiographyScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/angiography_score.html'
    template_name1 = 'zonal_offices/angiography_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AngiographyModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = AngiographyModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AngiographyModelForm(instance=obj)
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

    

class CarmScore(InspectionObjectMixin, View):
    template_name = 'zonal_offices/carm_score.html'
    template_name1 = 'zonal_offices/carm_score_details.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CarmModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        
        form = CarmModelForm(request.POST)
        if form.is_valid():
            form.save()
        
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CarmModelForm(instance=obj)
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





def mri(request, id):
  if request.method == 'POST':
    practice_manager = request.POST['practice_manager']
    shielding_score = request.POST['shielding_score']
    room_design_score = request.POST['room_design_score']
    radiographers_no_score = request.POST['radiographers_no_score']
    radiologists_no_score = request.POST['radiologists_no_score']
    radiographer_license_score = request.POST['radiographer_license_score']
    metal_screening_device_score = request.POST['metal_screening_device_score']
    screening_questionnaire_score = request.POST['screening_questionnaire_score']
    water_supply_score = request.POST['water_supply_score']
    accessories_adequacy_score = request.POST['accessories_adequacy_score']
    warning_signs_score = request.POST['warning_signs_score']
    C07_form_compliance_score = request.POST['C07_form_compliance_score']
    equipment_installation_location_score = request.POST['equipment_installation_location_score']
    processing_unit_score = request.POST['processing_unit_score']
    toilets_cleanliness_score = request.POST['toilets_cleanliness_score']
    waiting_room_score = request.POST['waiting_room_score']
    offices_adequacy_score = request.POST['offices_adequacy_score']
    technical_room_adequacy_score = request.POST['technical_room_adequacy_score']
    mri_total = request.POST['mri_total']



    mri = Mri(practice_manager=practice_manager, shielding_score=shielding_score, room_design_score=room_design_score, radiographers_no_score=radiographers_no_score, radiologists_no_score=radiologists_no_score, radiographer_license_score=radiographer_license_score, metal_screening_device_score=metal_screening_device_score, screening_questionnaire_score=screening_questionnaire_score, water_supply_score=water_supply_score, accessories_adequacy_score=accessories_adequacy_score, warning_signs_score=warning_signs_score, C07_form_compliance_score=C07_form_compliance_score, equipment_installation_location_score=equipment_installation_location_score, processing_unit_score=processing_unit_score, toilets_cleanliness_score=toilets_cleanliness_score, waiting_room_score=waiting_room_score, offices_adequacy_score=offices_adequacy_score, technical_room_adequacy_score=technical_room_adequacy_score, mri_total=mri_total )

    mri.save()





class AccreditationReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/accreditation_report_creation.html"
    template_name1 = "zonal_offices/accreditation_report_confirmation.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AccreditationModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)


    def post(self, request,  *args, **kwargs):
        form = AccreditationModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Notice of Facility Inspection'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'zonal_offices/accreditation_report.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        return render(request, self.template_name1, context)
        
        

class InspectionReportsView(LoginRequiredMixin, View):
    template_name = "zonal_offices/inspection_reports_list.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return self.queryset
        #return self.queryset
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)



def view_inspection_report(request, id):
  inspection = get_object_or_404(Inspection, pk=id)
  
  context={'inspection': inspection,
           
           }
  return render(request, 'zonal_offices/inspection_details.html', context)



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








class RegisteredHospitalsListView(LoginRequiredMixin, View):
    template_name = "zonal_offices/registered_hospitals_list.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


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
