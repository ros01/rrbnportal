from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import finance_required
from django.http import HttpResponse

@login_required
@finance_required
def index(request):
    return render (request, 'finance/finance_dashboard.html')
