from django.forms import ModelForm
from .models import AvailableTime




class AvailableTimeForm(ModelForm):
    class Meta:
        model = AvailableTime
        exclude = ["patient",]

