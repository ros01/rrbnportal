from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include ('pages.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('finance/', include('finance.urls')),
    path('registrars_office/', include ('registrars_office.urls')),
    path('zonal_offices/', include ('zonal_offices.urls')),
    path('utilities/', include ('utilities.urls')),
    path('captcha/', include ('captcha.urls')),








] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
