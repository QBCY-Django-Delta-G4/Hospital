from django.urls import path
from .views import create_patient

urlpatterns = [
    path('create_patient/', create_patient, name='create_patient'),
]
