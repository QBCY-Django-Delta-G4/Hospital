from django.db import models
from django.contrib.auth.models import User


class Specialization(models.Model):
    title = models.CharField(max_length=255)


class Doctor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    clinic_address = models.TextField()
    license_number = models.CharField(max_length=11)
    biography = models.TextField()
    is_active = models.BooleanField()
    visit_cost = models.DecimalField(max_digits=8)


class AvailableTime(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    


class Comment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='comments',blank=False,null=False)
    name = models.CharField(max_length=80,blank=False,null=False)
    email = models.EmailField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    is_visited = models.BooleanField(default=False)

class Rating(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, blank=False,null=False)
    score = models.PositiveIntegerField()



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10)
    phone = models.CharField(max_length=15)
    reserved_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)
