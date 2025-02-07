from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from hospitals.models import Payment, License
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import finance_required
from django.http import HttpResponse
from django.views import View
from . import views
from django.utils.decorators import method_decorator

@login_required
@finance_required
def index(request):
    return render (request, 'finance/finance_dashboard.html')




class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PaymentsListView(LoginRequiredMixin, View):
    template_name = "finance/payments_list.html"
    queryset = Payment.objects.all().order_by('-payment_date')

    def get_queryset(self):
        return self.queryset

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class PaymentDetailView(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "finance/payment_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class RegisteredHospitalsListView(LoginRequiredMixin, View):
    template_name = "finance/registered_hospitals_list.html"
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
    template_name = "finance/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


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


