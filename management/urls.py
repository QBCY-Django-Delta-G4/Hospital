from django.urls import path
from .views import *

urlpatterns = [
    path('create_patient/', create_patient, name='create_patient'),
    path('create_availableTime/',Create_AvailableTime,name='create_availableTime'),
    path('createdoctor/', create_doctor, name='createdoctor'),
    path('viewdoctor/', view_doctor, name='viewdoctor'),
    path('createspecialize/', create_specialize, name='createspecialize')
]
