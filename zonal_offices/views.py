from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import zonaloffices_required
from django.http import HttpResponse

@login_required
@zonaloffices_required
def index(request):
    return render (request, 'zonal_offices/zonal_offices_dashboard.html')

@login_required
def offices(request):
  return render(request, 'zonal_offices/rrbn_offices.html')
