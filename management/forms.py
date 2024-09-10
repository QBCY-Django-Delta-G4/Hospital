from django import forms
from .models import Patient,AvailableTime
from django.contrib.auth.models import User

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
        exclude = ["patient",]


