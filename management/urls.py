from django.urls import path
from .views import Create_AvailableTime


app_name='library'


urlpatterns = [
    path('create_availableTime/',Create_AvailableTime,name='create_availableTime'),
]

