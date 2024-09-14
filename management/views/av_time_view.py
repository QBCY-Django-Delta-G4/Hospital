from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from management.forms import *
from management.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from datetime import date
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger




@login_required(login_url='login')
def availabletime_doctor(request:HttpRequest,id):
    doctor = get_object_or_404(Doctor,id=id)
    availabletimes =  AvailableTime.objects.filter(doctor=doctor).order_by('-date')

    is_admin = False
    if request.user.is_staff: # is admin
        is_admin = True
    else: # is patient
        patient = get_object_or_404(Patient,user=request.user)
        today = date.today()
        availabletimes = availabletimes.filter(Q(patient=None)|Q(patient=patient))
        availabletimes = availabletimes.filter(Q(date__gte=today))

    paginator = Paginator(availabletimes,5)
    get_page  = request.GET.get('page')
    try:
        availabletimes = paginator.page(get_page)
    except PageNotAnInteger:
        availabletimes = paginator.page(1)
    except EmptyPage:
        availabletimes = paginator.page(paginator.num_pages)

    try:
        page_i = int(get_page)
    except:
        page_i = 1

    context = {
        "is_admin":is_admin,
        "doctor":doctor,
        "availabletimes":availabletimes,
        "page_i":page_i
    }
    return render(request,"av_time/availabletime_doctor.html",context=context)



@login_required(login_url='login')
@permission_required('management.add_availabletime', raise_exception=True)
def create_availabletime(request:HttpRequest,id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        AvailableTime.objects.create(date=date,start_time=start_time,end_time=end_time,doctor=doctor)
        msg = f'نوبت خالی برای دکتر {doctor.first_name} {doctor.last_name} اضافه شد.'
        messages.success(request, msg)
        return redirect("availabletime_doctor", id=id)
    return render(request, "av_time/create_availabletime.html", {'doctor':doctor})



@login_required(login_url='login')
@permission_required('management.edit_availabletime', raise_exception=True)
def edit_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    if request.method == "POST":
        availabletime.date = request.POST.get('date')
        availabletime.start_time = request.POST.get('start_time')
        availabletime.end_time = request.POST.get('end_time')
        availabletime.save()
        msg = f'نوبت خالی برای دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} اضافه شد.'
        messages.success(request, msg)
        return redirect("availabletime_doctor", id=availabletime.doctor.id)
    return render(request, "av_time/edit_availabletime.html", {"availabletime": availabletime})



@login_required(login_url='login')
@permission_required('management.delete_availabletime', raise_exception=True)
def delete_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    availabletime.delete()
    msg = f'نوبت خالی برای دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} حذف شد.'
    messages.success(request, msg)
    return redirect("availabletime_doctor", id=availabletime.doctor.id)
