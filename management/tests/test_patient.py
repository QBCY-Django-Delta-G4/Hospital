<<<<<<< HEAD
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from management.models import *
from django.utils import timezone
from django.contrib.messages import get_messages

class HomeViewTests(TestCase):
    def setUp(self):
        self.specialization = Specialization.objects.create(title="Dentist")

        Doctor.objects.create(first_name="Hasan", last_name="Ahmady", specializations=self.specialization, visit_cost=500, phone="123", clinic_address="Address", license_number=1, biography="bio")

        Doctor.objects.create(first_name="Matin", last_name="Amiri", specializations=self.specialization, visit_cost=500, phone="123", clinic_address="Address", license_number=2, biography="bio")

        self.user = User.objects.create_user(username='testuser', first_name="test", last_name='test', password='password', email='testuser@test.com')
        self.patient = Patient.objects.create(user=self.user,phone='1234567890')

    def test_home_view_without_login(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Hasan Ahmady')
        self.assertContains(response, 'Matin Amiri')
        self.assertContains(response, 'ورود')
        self.assertContains(response, 'ثبت نام')

    def test_home_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Hasan Ahmady')
        self.assertContains(response, 'Matin Amiri')

    def test_home_view_with_search(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('home') + '?q=Hasan')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hasan Ahmady')
        self.assertNotContains(response, 'Matin Amiri')

class CreatePatientViewTests(TestCase):
    def test_create_patient_get(self):
        response = self.client.get(reverse('create_patient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient/add_patient.html')

    def test_create_patient_post(self):
        data = {'username': 'testuser', 'first_name': 'امیر', 'last_name': 'احمدی', 'email': 'MrTester@test.com', 'password': 'password', 'phone': '09139111197'}
        response = self.client.post(reverse('create_patient') , data)
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('login'))

class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='oldpassword')
        self.client.login(username='testuser', password='oldpassword')

    def test_change_password(self):
        data = {'password': 'oldpassword', 'new_password': 'newpassword', 'confirm_new_password': 'newpassword',}
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
=======
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from management.models import *
from django.utils import timezone
from django.contrib.messages import get_messages

class HomeViewTests(TestCase):
    def setUp(self):
        self.specialization = Specialization.objects.create(title="Dentist")

        Doctor.objects.create(first_name="Hasan", last_name="Ahmady", specializations=self.specialization, visit_cost=500, phone="123", clinic_address="Address", license_number=1, biography="bio")

        Doctor.objects.create(first_name="Matin", last_name="Amiri", specializations=self.specialization, visit_cost=500, phone="123", clinic_address="Address", license_number=2, biography="bio")

        self.user = User.objects.create_user(username='testuser', first_name="test", last_name='test', password='password', email='testuser@test.com')
        self.patient = Patient.objects.create(user=self.user,phone='1234567890')

    def test_home_view_without_login(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Hasan Ahmady')
        self.assertContains(response, 'Matin Amiri')
        self.assertContains(response, 'ورود')
        self.assertContains(response, 'ثبت نام')

    def test_home_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Hasan Ahmady')
        self.assertContains(response, 'Matin Amiri')

    def test_home_view_with_search(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('home') + '?q=Hasan')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hasan Ahmady')
        self.assertNotContains(response, 'Matin Amiri')

class CreatePatientViewTests(TestCase):
    def test_create_patient_get(self):
        response = self.client.get(reverse('create_patient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient/add_patient.html')

    def test_create_patient_post(self):
        data = {'username': 'testuser', 'first_name': 'امیر', 'last_name': 'احمدی', 'email': 'MrTester@test.com', 'password': 'password', 'phone': '09139111197'}
        response = self.client.post(reverse('create_patient') , data)
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('login'))

class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='oldpassword')
        self.client.login(username='testuser', password='oldpassword')

    def test_change_password(self):
        data = {'password': 'oldpassword', 'new_password': 'newpassword', 'confirm_new_password': 'newpassword',}
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
>>>>>>> 92bea6eca2d24b59cf92a94d0934973e3b03cb75
        self.assertTrue(self.user.check_password('newpassword'))