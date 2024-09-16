from django.http import HttpRequest
from django.shortcuts import render, redirect
from management.forms import *
from management.models import *
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password






def patient_login(request:HttpRequest):
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

    return render(request, 'login/login.html', {'form': form})



def forgot_password_view(request:HttpRequest):
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



def reset_password_view(request:HttpRequest):
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



@login_required(login_url='login')
def patient_logout(request:HttpRequest):
    logout(request)
    messages.success(request, 'خارج شدید')
    return redirect('home')
