from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages


def create_doctor(request):
    if request.method == 'POST':
        forms = DoctorForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_doctor.html', {'forms': forms})
        else:
            forms.save()
            messages.success(request, 'ثبت شد')
            return redirect('createdoctor')
    else:
        forms = DoctorForm()

    return render(request, 'create_doctor.html', {'forms': forms})


def view_doctor(request):
    doctors = Doctor.objects.all()
    context = {
        'doctors': doctors
    }
    return render(request, 'view_doctor.html', context)


def create_specialize(request):
    if request.method == 'POST':
        forms = SpecializationForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_specialize.html', {'forms': forms})

        forms.save()
        messages.success(request, 'ثبت شد')
        return redirect('createdoctor')

    else:
        forms = SpecializationForm()

    return render(request, 'create_specialize.html', {'forms': forms})


def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('Done')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})


def Create_AvailableTime(request):
    if request.method == "POST":
        form = AvailableTimeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/create_availableTime/")

    else:
        form = AvailableTimeForm()

    return render(request, "Create_AvailableTime.html", {"form": form})




def create_comment(request):
    if request.method == 'POST':
        forms = CommentForm(request.POST)
        
        if not forms.is_valid():
            return render(request, 'create_commnet.html', {'forms': forms})

        forms.save()
        messages.success(request, 'ثبت شد')
        return redirect('create_rating')

    else:
        forms = CommentForm()

    return render(request, 'create_comment.html', {'forms': forms})



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