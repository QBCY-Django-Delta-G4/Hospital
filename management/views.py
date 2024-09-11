from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from .forms import *
from .models import *
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def create_doctor(request):
    if request.method == 'POST':
        forms = DoctorForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_doctor.html', {'forms': forms})
        else:
            forms.save()
            return redirect('viewdoctor')
    else:
        forms = DoctorForm()

    return render(request, 'create_doctor.html', {'forms': forms})

@login_required(login_url='login')
def view_doctor(request):
    doctors = Doctor.objects.filter(is_deleted=False)
    context = {
        'doctors': doctors
    }
    return render(request, 'view_doctor.html', context)

@login_required(login_url='login')
def create_specialize(request):
    if request.method == 'POST':
        forms = SpecializationForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_specialize.html', {'forms': forms})

        forms.save()
        messages.success(request, 'ثبت شد')
        return redirect('viewdoctor')

    else:
        forms = SpecializationForm()

    return render(request, 'create_specialize.html', {'forms': forms})

def create_patient(request):
    if request.user.is_authenticated:
        return redirect('viewdoctor')
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})



@login_required(login_url='login')
def create_availabletime(request:HttpRequest,id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        form = AvailableTimeForm(request.POST)

        if form.is_valid():
            fr = form.save(commit=False)
            fr.doctor = doctor
            fr.save()
            return redirect("availabletime_doctor", id=id)
    else:
        form = AvailableTimeForm()

    return render(request, "Create_AvailableTime.html", {"form": form})


@login_required(login_url='login')
def edit_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    if request.method == "POST":
        form = AvailableTimeForm(request.POST, instance=availabletime)
        if form.is_valid():
            form.save()
            return redirect("availabletime_doctor", id=availabletime.doctor.id)
    else:
        form = AvailableTimeForm(instance=availabletime)
    return render(request, "Create_AvailableTime.html", {"form": form})


@login_required(login_url='login')
def delete_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    availabletime.delete()
    return redirect("availabletime_doctor", id=availabletime.doctor.id)




@login_required(login_url='login')
def create_comment(request):
    if request.method == 'POST':
        forms = CommentForm(request.POST)
        
        if not forms.is_valid():
            return render(request, 'detail_doctor.html', {'forms': forms})

        forms.save()
        messages.success(request, 'ثبت شد')
        return redirect('create_rating')

    else:
        forms = CommentForm()

    return render(request, 'create_comment.html', {'forms': forms})


@login_required(login_url='login')
def create_rating(request):
    if request.method == "POST":
        form = RatingForm(request.POST) 

        if form.is_valid():
            messages.success(request, 'ثبت شد')
            form.save()
            return redirect("create_rating")

    else:
        form = RatingForm()

    return render(request, "create_rating.html", {"form": form})

@login_required(login_url='login')
def doctor_timelist(request, pk):
    pass

@login_required(login_url='login')
def delete_doctor(request, id):
    doctor = Doctor.objects.get(id=id)
    doctor.is_deleted = True
    doctor.save()
    return redirect("viewdoctor")

@login_required(login_url='login')
def edit_doctor(request, id):
    doctor = Doctor.objects.get(pk=id)
    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('viewdoctor')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'edit_doctor.html', {'forms': form})

@login_required(login_url='login')
def detail_doctor(request, id):
    doctors = Doctor.objects.get(id=id)
    context = {
        'doctors': doctors
    }
    return render(request, 'detail_doctor.html', context)



@login_required(login_url='login')
def availabletime_doctor(request:HttpRequest,id):
    doctor = get_object_or_404(Doctor,id=id)
    availabletimes =  AvailableTime.objects.filter(doctor=doctor)

    context = {
        "doctor":doctor,
        "availabletimes":availabletimes
    }
    return render(request,"availabletime_doctor.html",context=context)




def patient_login(request):
    if request.method == 'POST':
        form = LoginAsPatient(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('createdoctor')
    else:
        form = LoginAsPatient()

    return render(request, 'login.html', {'form': form})

def home(request):
    doctors = Doctor.objects.all()
    search_query = request.GET.get('q')

    if search_query:

        doctors = doctors.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(specializations__title__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )

    context = {
        'doctors':doctors
    }

    return render(request, 'home.html', context)

@login_required(login_url='login')
def patient_logout(request):
    logout(request)
    return redirect('home')

