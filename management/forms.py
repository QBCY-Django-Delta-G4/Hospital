from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
import re
from django.core.exceptions import ValidationError


def check_name(name):
    name_regex = r'^[\u0600-\u06FF\s]+$'
    if not re.match(name_regex, name):
        return False
    return True


def check_phone(phone):
    phone_regex = r'^09[0-9]{9}$'
    print(phone)
    if not re.match(phone_regex, phone):
        return False
    return True


def validate_jpg(value):
    if not value.name.lower().endswith(('.jpg', 'jpeg')):
        raise ValidationError('فقط فایل‌های با فرمت jpg مجاز هستند.')


def validate_image_size(value):
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024

    if value.size > max_size_bytes:
        raise ValidationError(f'حجم فایل نباید بیش از {max_size_mb} مگابایت باشد.')


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name',
                  'specializations', 'image', 'phone',
                  'clinic_address', 'license_number',
                  'biography', 'visit_cost', 'is_active',
                  ]

    first_name = forms.CharField(label='نام دکتر')
    last_name = forms.CharField(label='نام خانوادگی')
    phone = forms.CharField(label='شماره تماس')
    license_number = forms.IntegerField(label='شماره نظام پزشکی')
    visit_cost = forms.DecimalField(label='هزینه ویزیت')

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_jpg(image)
            validate_image_size(image)
        return image

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not check_name(first_name):
            raise forms.ValidationError('نام را با کاراکتر حروف بنویسید')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not check_name(last_name):
            raise forms.ValidationError('نام خانوادگی را با کاراکتر حروف بنویسید.')
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not check_phone(phone):
            raise forms.ValidationError('لطفا شماره تماس را به درستی وارد نمایید.')
        return phone


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ['title']


class PatientForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=15)

    class Meta:
        model = Patient
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not check_name(first_name):
            raise forms.ValidationError('نام را با کاراکتر حروف بنویسید')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not check_name(last_name):
            raise forms.ValidationError('نام خانوادگی را با کاراکتر حروف بنویسید.')
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not check_phone(phone):
            raise forms.ValidationError('لطفا شماره تماس را به درستی وارد نمایید.')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        patients = Patient.objects.filter(user__email=email)
        if patients:
            raise forms.ValidationError('این ایمیل قبلا ثبت شده است')

        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        patients = Patient.objects.filter(user__username=username)
        if patients:
            raise forms.ValidationError("این نام کاربری از قبل ثبت شده است")

        return username

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        patient = super(PatientForm, self).save(commit=False)
        patient.user = user
        if commit:
            patient.save()
        return patient


class AvailableTimeForm(forms.ModelForm):
    class Meta:
        model = AvailableTime
        exclude = ["patient", "doctor"]


class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='پسورد اکانت')
    new_password = forms.CharField(widget=forms.PasswordInput, required=True, label='پسورد جدید')
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, required=True, label='تکرار پسورد جدید')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError("پسورد غلط است.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError("پسوردهای جدید یکی نیست!")
        return cleaned_data


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'description': 'امتیاز'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'نظر خود را اینجا بنویسید...'})
        }
        labels = {
            'description': 'نظر شما'
        }


class LoginAsPatient(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class PatientAddBalanceForm(forms.Form):
    balance = forms.DecimalField(min_value=0.0)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    code = forms.CharField(max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput)


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='نام')
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                label='نام خانوادگی')
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}), label='ایمیل')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not check_name(first_name):
            raise forms.ValidationError('نام را با کاراکتر حروف بنویسید')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not check_name(last_name):
            raise forms.ValidationError('نام خانوادگی را با کاراکتر حروف بنویسید.')
        return last_name

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class EditPatientForm(forms.ModelForm):
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='شماره تماس')

    class Meta:
        model = Patient
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not check_phone(phone):
            raise forms.ValidationError('لطفا شماره تماس را به درستی وارد نمایید.')
        return phone
