from django.urls import path
from .views import create_patient,Create_AvailableTime

urlpatterns = [
    path('create_patient/', create_patient, name='create_patient'),
    path('create_availableTime/',Create_AvailableTime,name='create_availableTime'),
]
