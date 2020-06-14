from django.shortcuts import render
from django.http import HttpResponse
from hospitals.models import License
from django.db.models import Q
from django.views.generic import TemplateView, ListView

def index(request):
    return render(request, 'pages/index.html')

def verify_practice(request):
    return render(request, 'pages/verify_practice.html')

class SearchResultsView(ListView):
    model = License
    template_name = 'search_result.html'
    
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list = License.objects.filter(
            Q(license_no__icontains=query) | Q(hospital_name__icontains=query)
        )
        return object_list



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
