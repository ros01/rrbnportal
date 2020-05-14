from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'pages/index.html')


def about(request):
    return render(request, 'pages/about.html')

def get_object_or_404(request):
    return render(request, 'pages/404.html')

def contact(request):
    return render(request, 'pages/contact.html')

def mission(request):
    return render(request, 'pages/mission.html')

def mandate(request):
    return render(request, 'pages/mandate.html')

def benefits(request):
    return render(request, 'pages/benefits.html')

def faq(request):
    return render(request, 'pages/faq.html')

def guidelines(request):
    return render(request, 'pages/guidelines.html')

def internship_centers(request):
    return render(request, 'pages/internship_centers.html')

def zonal_offices(request):
    return render(request, 'pages/zonal_offices.html')
