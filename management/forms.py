from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
import re


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name',
                  'specializations', 'phone',
                  'clinic_address', 'license_number',
                  'biography','visit_cost','is_active',
                 ]

    first_name = forms.CharField(label='نام دکتر')
    last_name = forms.CharField(label='نام خانوادگی')
    phone = forms.CharField(label='شماره تماس')
    license_number = forms.CharField(label='شماره نظام پزشکی')
    visit_cost = forms.DecimalField(label='نوبت دهی')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        first_name_regex = r'^[\u0600-\u06FF\s]+$'
        if not re.match(first_name_regex, first_name):
            raise forms.ValidationError('نام را با کاراکتر حروف بنویسید')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        last_name_regex = r'^[\u0600-\u06FF\s]+$'
        if not re.match(last_name_regex, last_name):
            raise forms.ValidationError('نام خانوادگی را با کاراکتر حروف بنویسید.')

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_regex = r'^09[0-9]{9}$'
        if not re.match(phone_regex, phone):
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
        exclude = ["patient","doctor"]


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