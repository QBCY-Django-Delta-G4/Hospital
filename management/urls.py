from django.urls import path
from .views import *

urlpatterns = [
    path('create_patient/', create_patient, name='create_patient'),
    path('createdoctor/', create_doctor, name='createdoctor'),
    path('viewdoctor/', view_doctor, name='viewdoctor'),
    path('createspecialize/', create_specialize, name='createspecialize'),
    path('create_comment/', create_comment, name='create_comment'),
    path('create_rating/', create_rating, name='create_rating'),
    path('timelist/<int:id>/', doctor_timelist, name='doctor_timelist'),
    path('delete_doctor/<int:id>/', delete_doctor, name='delete_doctor'),
    path('detail_doctor/<int:id>/', detail_doctor, name='detail_doctor'),
    path('edit_doctor/<int:id>/', edit_doctor, name='edit_doctor'),
    path('availabletime_doctor/<int:id>/', availabletime_doctor, name='availabletime_doctor'),
    path('create_availabletime/<int:id>/', create_availabletime, name='create_availabletime'),
    path('edit_availabletime/<int:id>/', edit_availabletime, name='edit_availabletime'),
    path('delete_availabletime/<int:id>/', delete_availabletime, name='delete_availabletime'),
    path('login/', patient_login, name="login" ),
    path('logout/', patient_logout, name="logout" ),
    path('', home, name="home")
]
