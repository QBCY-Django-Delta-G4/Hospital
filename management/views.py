from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import *
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q, Value
from django.db.models.functions import Concat
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password



@login_required(login_url='login')
@permission_required('management.add_doctor', raise_exception=True)
def create_doctor(request):
    if request.method == 'POST':
        forms = DoctorForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_doctor.html', {'forms': forms})
        else:
            forms.save()
            msg = f'دکتر {forms.cleaned_data["first_name"]} {forms.cleaned_data["last_name"]} اضافه شد.'
            messages.success(request, msg)
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
@permission_required('management.add_specialization', raise_exception=True)
def create_specialize(request):
    if request.method == 'POST':
        forms = SpecializationForm(request.POST)
        if not forms.is_valid():
            return render(request, 'create_specialize.html', {'forms': forms})

        forms.save()
        msg = f'تخصص {forms.cleaned_data["title"]} اضافه شد.'
        messages.success(request, msg)
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
            msg = f'بیمار {forms.cleaned_data["first_name"]} {forms.cleaned_data["last_name"]} اضافه شد.'
            messages.success(request, msg)
            return redirect('login')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})


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
    return render(request, "Create_AvailableTime.html", {'doctor':doctor})


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
    return render(request, "edit_availabletime.html", {"availabletime": availabletime})


@login_required(login_url='login')
@permission_required('management.delete_availabletime', raise_exception=True)
def delete_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    availabletime.delete()
    msg = f'نوبت خالی برای دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} حذف شد.'
    messages.success(request, msg)
    return redirect("availabletime_doctor", id=availabletime.doctor.id)





@login_required(login_url='login')
@permission_required('management.add_rating', raise_exception=True)
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
@permission_required('management.delete_doctor', raise_exception=True)
def delete_doctor(request, id):
    doctor = Doctor.objects.get(id=id)
    doctor.is_deleted = True
    doctor.save()
    msg = f'دکتر {doctor.first_name} {doctor.last_name} حذف شد.'
    messages.success(request, msg)
    return redirect("viewdoctor")


@login_required(login_url='login')
@permission_required('management.change_doctor', raise_exception=True)
def edit_doctor(request, id):
    doctor = Doctor.objects.get(pk=id)
    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            msg = f'دکتر {doctor.first_name} {doctor.last_name} ویرایش شد.'
            messages.success(request, msg)
            return redirect('viewdoctor')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'edit_doctor.html', {'forms': form})


@login_required(login_url='login')
def detail_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    comments = doctor.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.doctor = doctor
            try:
                patient = Patient.objects.get(user=request.user)
                new_comment.patient = patient
                new_comment.save()
                messages.success(request, 'نظر شما با موفقیت ثبت شد.')
                return redirect('detail_doctor', id=id)  # به صفحه دکتر هدایت می‌شود تا نظر جدید نمایش داده شود
            except Patient.DoesNotExist:
                messages.error(request, 'بیمار مربوطه یافت نشد.')
    else:
        comment_form = CommentForm()

    context = {
        'doctor': doctor,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form
    }

    return render(request, 'detail_doctor.html', context)


# @login_required(login_url='login')
# @permission_required('management.add_comment', raise_exception=True)
# def create_comment(request):
#     if request.method == 'POST':
#         forms = CommentForm(request.POST)
#
#         if not forms.is_valid():
#             return render(request, 'detail_doctor.html', {'forms': forms})
#
#         forms.save()
#         messages.success(request, 'ثبت شد')
#         return redirect('create_rating')
#
#     else:
#         forms = CommentForm()
#
#     return render(request, 'create_comment.html', {'forms': forms})


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

    context = {
        "is_admin":is_admin,
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
            msg = f'با نام کاربری {user.username} وارد شدید.'
            messages.success(request, msg)
            return redirect('home')
    else:
        form = LoginAsPatient()

    return render(request, 'login.html', {'form': form})


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


@login_required(login_url='login')
def patient_logout(request):
    logout(request)
    messages.success(request, 'خارج شدید')
    return redirect('home')


@login_required(login_url='login')
def patient_reservation(request,id):
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

    msg = f'نوبت دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} برای شما رزرو شد.'
    messages.success(request, msg)

    return redirect("availabletime_doctor",id=availabletime.doctor.id)


@login_required(login_url='login')
def patient_add_balance(request):
    patient = get_object_or_404(Patient,user=request.user)
    if request.method == "POST":
        form = PatientAddBalanceForm(request.POST)
        if form.is_valid():
            balance = form.cleaned_data["balance"]
            patient.balance = patient.balance + balance
            patient.save()
            msg = f'مبلغ {balance} به کبف پول شما اضافه شد.'
            messages.success(request, msg)
            return redirect('home')
    else:
        form = PatientAddBalanceForm()
    return render(request, 'patient_add_balance.html', {'forms': form})


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
        msg = f'نوبت دکتر {availabletime.doctor.first_name} {availabletime.doctor.last_name} برای شما حذف شد و مبلغ ویزیت به کیف پول شما اضافه گردید.'
        messages.success(request, msg)

    if r == 1:
        return redirect('patient_reserved_times')
    elif r == 2:
        return redirect('availabletime_doctor',availabletime.doctor.id)


@login_required(login_url='login')
def patient_reserved_times(request):
    patient = get_object_or_404(Patient,user=request.user)
    availabletimes = AvailableTime.objects.filter(patient=patient).order_by('-date')

    context = {"availabletimes":availabletimes,}
    return render(request,"patient_reserved_times.html",context=context)


@login_required(login_url='login')
def patient_profile(request):
    patient = get_object_or_404(Patient,user=request.user)
    # patient, created = Patient.objects.get_or_create(user=request.user)
    return render(request, 'patient_profile.html', {'patient': patient})






def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid:
            email = form.data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این ایمیل یافت نشد.')
                return redirect('forgot_password')
            
            reset_code = PasswordResetCode.objects.create(user=user)
            request.session['reset_user_id'] = user.id
            # send email
            subject = 'بازیابی رمز عبور'
            message = f'کد تایید شما: {reset_code.code}\n نام کاربری شما: {user.username}'
            from_mail = "test_mail@django.com"
            recipient_list = [user.email]
            
            send_mail(
                subject,
                message,
                from_mail,
                recipient_list,
                fail_silently=False,
            )
            
            messages.success(request, 'کد تأیید به ایمیل شما ارسال شد.')
            return redirect('reset_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


def reset_password_view(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            code = form.data['code']
            new_password = form.data['new_password']

            try:
                reset_code = PasswordResetCode.objects.get(code=code)
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'کد تأیید نامعتبر است.')
                return redirect('reset_password')

            id = request.session.get('reset_user_id')
            user = reset_code.user
            if id != user.id:
                messages.error(request, 'کد تأیید نامعتبر است.')
                return redirect('reset_password')
            
            user.password = make_password(new_password)
            user.save()
            reset_code.delete()

            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد.')
            return redirect('login')

    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})
