from django import template
from django.shortcuts import get_object_or_404
from ..models import *
from django.db.models import Q


register=template.Library()


@register.simple_tag
def date_format(date):
    return date.strftime("%Y.%m.%d")

@register.simple_tag
def inp_date_format(date):
    return date.strftime("%Y-%m-%d")

@register.simple_tag
def time_format(date):
    return date.strftime("%H:%M")

@register.simple_tag
def datetime_format(date):
    return date.strftime("%Y.%m.%d %H:%M")

@register.simple_tag
def patient_balance(user:User):
    patient = get_object_or_404(Patient,user=user)
    return patient.balance

@register.simple_tag
def get_patient_score(patient,doctor_id):
    try:
        score = Rating.objects.get(doctor__id=doctor_id,patient=patient)
        return score.score
    except:
        return "-"

