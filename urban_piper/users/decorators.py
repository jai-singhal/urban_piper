from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def storage_manager_req(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts/login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_storage_manager,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def delivery_person_req(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts/login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_delivery_person,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator