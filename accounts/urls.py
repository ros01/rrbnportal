from . import views
from django.urls import path
from .views import (
    RenewalCreateView, StartView, StartReg, SignUpView, StartIntershipApplication, ActivateAccount, ProfileUpdateView, LoginTemplateView, RenewalView, SearchResultsView
    
)


from django.contrib.auth.views import PasswordResetView

from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'accounts'






urlpatterns = [
    #path('validate_captcha', views.validate_captcha, name='validate_captcha'),
    #path('verify_practice', views.verify_practice, name='verify_practice'),
    #path('search/', SearchResultsView.as_view(), name='search_result'),
    path('start/', views.StartView.as_view(), name='start-reg'),
    path('start_registration/', views.StartReg.as_view(), name='start_registration'),
    path('signup/', SignUpView.as_view(), name='create_profile'),
    path('start_intership_application/', StartIntershipApplication.as_view(), name='create_manager_profile'),
    path('signin', LoginTemplateView.as_view(), name='signin'),
    #path('renewal/', views.renewal, name='renewal'),
    #path('delete/<license_id>', RenewalModelForm, views.delete, name="delete")
    #path('renewal', RenewalView.as_view(), name='renewal'),
    #path('search/', SearchResultsView.as_view(), name='search_result'),

    #path('renewal/', RenewalCreateView.as_view(), name='renewal'),
    path('activate_account', views.activate_account, name='activate_account'),
    path('renewal/', views.renewal, name='renewal'),
    #path('<int:id>/profile_details/', views.profile_details, name='profile_details'),
    #path('search', views.search, name='search'),
    #path('renewal', RenewalTemplateView.as_view(), name='renewal'),
    #path('accounts/profile/<username>/', ProfileDetailView.as_view(), name="to_profile"),
    #path('<int:id>/', views.profile_detail, name='profile_detail'),
    path('<int:id>/update_profile/', ProfileUpdateView.as_view(), name='update_profile'),
    #path('<int:id>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('login', views.login, name='login'),
    path('activate/<slug:uidb64>/<slug:token>/', ActivateAccount.as_view(), name='activate'),
    path('logout', views.logout, name='logout'),
    #path('reset-password', PasswordResetView.as_view(), name='password_reset'),
    #path('reset-password/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    #path('reset-password/confirm/<uidb64>[0-9A-Za-z]+)-<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset-password/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-done/', views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    #path('reset/<uuid:uidb64>/<slug:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    #RenewalTemplateView, SearchResultsView
    #path('signup/', views.Signup.as_view(), name='create_profile'),
    #path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    #path('activate/<str:uid>/<str:token>', views.Activate.as_view(), name='activate'),

]

