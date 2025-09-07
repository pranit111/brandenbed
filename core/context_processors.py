# core/context_processors.py
from django.conf import settings

def company_info(request):
    return {
        'company_name': settings.COMPANY_NAME,
        'company_phone': settings.COMPANY_PHONE,
        'company_email': settings.COMPANY_EMAIL,
        'company_address': settings.COMPANY_ADDRESS,
    }