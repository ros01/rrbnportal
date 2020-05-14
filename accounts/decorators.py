from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def registrar_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='404'):
    '''
    Decorator for views that checks that the logged in user is the registrar,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role=='Registrar',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def monitoring_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='404'):
    '''
    Decorator for views that checks that the logged in user is the registrar,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role=='Monitoring',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def zonaloffices_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='404'):
    '''
    Decorator for views that checks that the logged in user is in zonal office,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role=='Zonal Offices',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def finance_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='404'):
    '''
    Decorator for views that checks that the logged in user is the registrar,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role=='Finance',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
