from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from hospitals.models import Payment
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import finance_required
from django.http import HttpResponse
from django.views import View
from . import views

@login_required
@finance_required
def index(request):
    return render (request, 'finance/finance_dashboard.html')


class PaymentsListView(View):
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


class PaymentDetailView(PaymentObjectMixin, View):
    template_name = "finance/payment_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)
