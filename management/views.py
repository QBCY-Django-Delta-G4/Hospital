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
from django.core.paginator import Paginator




@login_required(login_url='login')
@permission_required('management.add_doctor', raise_exception=True)
def create_doctor(request):
    if request.method == 'POST':
        forms = DoctorForm(request.POST)
        if not forms.is_valid():
            return render(request, 'doctor/create_doctor.html', {'forms': forms})
        else:
            forms.save()
            messages.success(request, 'ثبت شد')
            return redirect('viewdoctor')
    else:
        forms = DoctorForm()

    return render(request, 'doctor/create_doctor.html', {'forms': forms})


@login_required(login_url='login')
def view_doctor(request):
    doctors = Doctor.objects.filter(is_deleted=False)
    context = {
        'doctors': doctors
    }
    return render(request, 'doctor/view_doctor.html', context)


@login_required(login_url='login')
@permission_required('management.add_specialization', raise_exception=True)
def create_specialize(request):
    if request.method == 'POST':
        forms = SpecializationForm(request.POST)
        if not forms.is_valid():
            return render(request, 'doctor/create_specialize.html', {'forms': forms})

        forms.save()
        messages.success(request, 'ثبت شد')
        return redirect('viewdoctor')

    else:
        forms = SpecializationForm()

    return render(request, 'doctor/create_specialize.html', {'forms': forms})


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
    return render(request, 'patient/add_patient.html', {'form': form})


@login_required(login_url='login')
@permission_required('management.add_availabletime', raise_exception=True)
def create_availabletime(request:HttpRequest,id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        AvailableTime.objects.create(date=date,start_time=start_time,end_time=end_time,doctor=doctor)

        return redirect("availabletime_doctor", id=id)
    return render(request, "avtime/Create_AvailableTime.html", {'doctor':doctor})


@login_required(login_url='login')
@permission_required('management.edit_availabletime', raise_exception=True)
def edit_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    if request.method == "POST":
        availabletime.date = request.POST.get('date')
        availabletime.start_time = request.POST.get('start_time')
        availabletime.end_time = request.POST.get('end_time')
        availabletime.save()
        return redirect("availabletime_doctor", id=availabletime.doctor.id)
    return render(request, "avtime/edit_availabletime.html", {"availabletime": availabletime})


@login_required(login_url='login')
@permission_required('management.delete_availabletime', raise_exception=True)
def delete_availabletime(request:HttpRequest,id):
    availabletime = AvailableTime.objects.get(pk=id)
    availabletime.delete()
    return redirect("availabletime_doctor", id=availabletime.doctor.id)





@login_required(login_url='login')
@permission_required('management.delete_doctor', raise_exception=True)
def delete_doctor(request, id):
    doctor = Doctor.objects.get(id=id)
    doctor.is_deleted = True
    doctor.save()
    return redirect("viewdoctor")


@login_required(login_url='login')
@permission_required('management.change_doctor', raise_exception=True)
def edit_doctor(request, id):
    doctor = Doctor.objects.get(pk=id)
    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('viewdoctor')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctor/edit_doctor.html', {'forms': form})


@login_required(login_url='login')
# @permission_required('management.change_doctor', raise_exception=True)
def detail_doctor(request, id):
    doctors = get_object_or_404(Doctor, id=id)
    comments = doctors.comments.filter(is_deleted=False, active=True)

    paginator = Paginator(comments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    new_comment = None
    rating_form = RatingForm()
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.doctor = doctors
            try:
                patient = Patient.objects.get(user=request.user)
                new_comment.patient = patient
                new_comment.save()
                messages.success(request, 'نظر شما با موفقیت ارسال شد.')
                return redirect('detail_doctor', id=id)
            except Patient.DoesNotExist:
                messages.error(request, 'بیمار مربوطه یافت نشد')
                return redirect('detail_doctor', id=id)
    else:
        comment_form = CommentForm()

    context = {
        'doctors': doctors,
        'page_obj': page_obj,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'is_admin': request.user.is_staff,
    }
    return render(request, 'doctor/detail_doctor.html', context)



def add_rating(request, doctor_id):
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, id=doctor_id)
        patient = get_object_or_404(Patient,
                                    user=request.user)
        score = request.POST.get('score')


        rating, created = Rating.objects.get_or_create(
            doctor=doctor,
            patient=patient,
            defaults={'score': score}
        )

        if not created:
            rating.score = score
            rating.save()

        return redirect('doctor_detail', doctor_id=doctor.id)

def delete_comment(request, doctor_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_authenticated:
        if request.user.is_staff or (comment.patient.user == request.user):
            comment.is_deleted = True
            comment.save()
            messages.success(request, 'نظر با موفقیت حذف شد.')
        else:
            messages.error(request, 'شما مجاز به حذف این نظر نیستید.')
    else:
        messages.error(request, 'ابتدا وارد حساب کاربری خود شوید.')

    return redirect('detail_doctor', id=doctor_id)


# @login_required(login_url='login')
# @permission_required('management.add_rating', raise_exception=True)
# def create_rating(request):
#     if request.method == "POST":
#         form = RatingForm(request.POST)
#         if form.is_valid():
#             rating = form.save(commit=False)
#
#             rating.patient = request.user.patient
#             form.save()
#             messages.success(request, 'امتیاز شما ثبت شد')
#             return redirect("detail_doctor")
#
#     else:
#         form = RatingForm()
#     return render(request, 'doctor/detail_doctor.html', {'form': form})

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
    return render(request,"avtime/availabletime_doctor.html",context=context)



def patient_login(request):
    if request.method == 'POST':
        form = LoginAsPatient(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginAsPatient()

    return render(request, 'login/login.html', {'form': form})


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

    return render(request, 'login/home.html', context)


@login_required(login_url='login')
def patient_logout(request):
    logout(request)
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
            return redirect('home')
    else:
        form = PatientAddBalanceForm()
    return render(request, 'patient/patient_add_balance.html', {'forms': form})


@login_required(login_url='login')
def patient_delete_reserve_time(request,id):
    availabletime = get_object_or_404(AvailableTime,id=id)
    patient = get_object_or_404(Patient,user=request.user)

    if availabletime.patient == patient:
        availabletime.patient = None
        availabletime.save()

        cost = availabletime.doctor.visit_cost
        patient_balance = patient.balance
        patient.balance = patient_balance + cost
        patient.save()

    return redirect('patient_reserved_times')


@login_required(login_url='login')
def patient_reserved_times(request):
    patient = get_object_or_404(Patient,user=request.user)
    availabletimes = AvailableTime.objects.filter(patient=patient).order_by('-date')

    context = {"availabletimes":availabletimes,}
    return render(request,"patient/patient_reserved_times.html",context=context)

@login_required(login_url='login')
def patient_profile(request):
    patient, created = Patient.objects.get_or_create(user=request.user)
    return render(request, 'patient/patient_profile.html', {'patient': patient})






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
    return render(request, 'login/forgot_password.html', {'form': form})


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

    return render(request, 'login/reset_password.html', {'form': form})
