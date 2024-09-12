from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator



class Specialization(models.Model):
    title = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.title


class Doctor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    specializations = models.ForeignKey(Specialization, on_delete=models.PROTECT, verbose_name='تخصص')
    phone = models.CharField(max_length=15)
    clinic_address = models.TextField(verbose_name='آدرس مطب')
    license_number = models.CharField(max_length=11)
    biography = models.TextField(verbose_name='درباره دکتر')
    is_active = models.BooleanField(default=True)
    visit_cost = models.DecimalField(decimal_places=2, max_digits=8)
    is_deleted = models.BooleanField(default=False, verbose_name='حذف شده')

    def __str__(self) -> str:
        return self.first_name


class AvailableTime(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    patient = models.ForeignKey("Patient", on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        permissions = [
            ("admin_available_time", "Can add-edit-remove available time"),
            ("patient_available_time", "Can view available time"),
        ]


class Comment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='comments', blank=False, null=False)
    patient = models.ForeignKey("Patient",on_delete=models.CASCADE,blank=True,null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    is_visited = models.BooleanField(default=False)

class Rating(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, blank=True, null=True)
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=15)

