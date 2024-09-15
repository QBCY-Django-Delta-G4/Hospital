from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from management.forms import *
from management.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout





def home(request):
    doctors = Doctor.objects.filter(is_deleted=False)
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



def create_patient(request):
    if request.user.is_authenticated:
        return redirect('viewdoctor')
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            msg = f'بیمار {form.cleaned_data["first_name"]} {form.cleaned_data["last_name"]} اضافه شد.'
            messages.success(request, msg)
            return redirect('login')
    else:
        form = PatientForm()
    return render(request, 'patient/add_patient.html', {'form': form})



@login_required(login_url='login')
def patient_reservation(request:HttpRequest,id):
    availabletime = get_object_or_404(AvailableTime,id=id)
    if availabletime.patient is None:
        patient = get_object_or_404(Patient,user=request.user)
        patient_balance = patient.balance
        cost = availabletime.doctor.visit_cost

        if patient_balance >= cost:
            patient.balance = patient_balance - cost
            availabletime.patient = patient
            availabletime.save()
            patient.save()

            # send email
            subject = 'رزور ثبت شد.'
            message = 'روز شما با موفقیت برای دکتر' + '\n' + availabletime.doctor.first_name + ' ' + availabletime.doctor.last_name + '\n' + 'در تاریخ و ساعت : ' + str(availabletime.date) + '\n' + str(availabletime.start_time) + '\n' + str(availabletime.end_time) + '\n ثبت شد.'
            from_mail = "test_mail@django.com"
            recipient_list = [request.user.email]

            send_mail(
                subject,
                message,
                from_mail,
                recipient_list,
                fail_silently=False,
            )
            msg = f'نوبت دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} برای شما رزرو شد و مبلغ {availabletime.doctor.visit_cost} تومان از کیف پول شما کسر شد.'
            messages.success(request, msg)

        else:
            msg = f"موجوی کافی نیست! \n لطفا ابتدا کیف پول خود را شارژ کنید."
            messages.error(request,msg)



    return redirect("availabletime_doctor",id=availabletime.doctor.id)



@login_required(login_url='login')
def patient_add_balance(request:HttpRequest):
    patient = get_object_or_404(Patient,user=request.user)
    if request.method == "POST":
        form = PatientAddBalanceForm(request.POST)
        if form.is_valid():
            balance = form.cleaned_data["balance"]
            patient.balance = patient.balance + balance
            patient.save()
            msg = f'مبلغ {balance} تومان به کبف پول شما اضافه شد.'
            messages.success(request, msg)
            return redirect('home')
    else:
        form = PatientAddBalanceForm()
    return render(request, 'patient/patient_add_balance.html', {'forms': form})



@login_required(login_url='login')
def patient_delete_reserve_time(request:HttpRequest,id,r):
    availabletime = get_object_or_404(AvailableTime,id=id)
    patient = get_object_or_404(Patient,user=request.user)

    if availabletime.patient == patient:
        availabletime.patient = None
        availabletime.save()

        cost = availabletime.doctor.visit_cost
        patient_balance = patient.balance
        patient.balance = patient_balance + cost
        patient.save()
        msg = f'نوبت دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} برای شما حذف شد و مبلغ {availabletime.doctor.visit_cost} تومان به کیف پول شما اضافه گردید.'
        messages.success(request, msg)

    if r == 1:
        return redirect('patient_reserved_times')
    elif r == 2:
        return redirect('availabletime_doctor',availabletime.doctor.id)



@login_required(login_url='login')
def patient_reserved_times(request:HttpRequest):
    patient = get_object_or_404(Patient,user=request.user)
    availabletimes = AvailableTime.objects.filter(patient=patient).order_by('-date')

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


    context = {"availabletimes":availabletimes,'page_i':page_i}
    return render(request,"patient/patient_reserved_times.html",context=context)



@login_required(login_url='login')
def patient_profile(request:HttpRequest):
    patient = get_object_or_404(Patient,user=request.user)
    return render(request, 'patient/patient_profile.html', {'patient': patient})


@login_required(login_url='login')
def edit_patient_profile(request):
    user = request.user  
    patient = request.user.patient  
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        patient_form = EditPatientForm(request.POST, instance=patient)

        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد.')
            return redirect('patient_profile')
    else:
        user_form = EditUserForm(instance=user)
        patient_form = EditPatientForm(instance=patient)

    return render(request, 'patient/edit_patient_profile.html', {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
    })


@login_required(login_url='login')
def change_password(request:HttpRequest):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get("new_password")
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "پسورد عوض شد!")
            logout(request)
            return redirect('login')
        else:
            messages.error(request, "مشکلی در تغییر پسورد پیش اومد. دوباره تلاش کنید.")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'patient/change_password.html', {'form': form})