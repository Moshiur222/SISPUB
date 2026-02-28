from .models import *
from django.urls import reverse

def company_info(request):
    return {
        'all_company_info': Company_info.objects.all(),
        'co_sponsers': Co_sponsers.objects.all()
    }


def global_seo(request):
    return {
        "seos": Seo.objects.all()
    }