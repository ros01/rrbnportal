from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import registrar_required


@login_required
@registrar_required  
def index(request):
    return render (request, 'registrars_office/registrar_dashboard.html')
