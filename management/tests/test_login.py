from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from management.forms import *
from django.core import mail
from management.models import *
from django.contrib.auth.hashers import check_password

class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', first_name="test", last_name='test', password='password', email='testuser@test.com')
        self.patient = Patient.objects.create(user=self.user,phone='1234567890')
    
    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')
        self.assertIsInstance(response.context['form'], LoginAsPatient)

    def test_ok_login_post(self):
        response = self.client.post(reverse('login'), {'username': 'testuser','password':'password'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,reverse('home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_bad_login_post(self):
        response = self.client.post(reverse('login'),{'username': 'testuser','password':'wrong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'login/login.html')

class ForgotPasswordViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', first_name="test", last_name='test', password='password', email='testuser@test.com')
        self.patient = Patient.objects.create(user=self.user,phone='1234567890')
    
    def test_forgot_password_get(self):
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/forgot_password.html')
        self.assertIsInstance(response.context['form'], ForgotPasswordForm)

    def test_ok_forgot_password_post(self):
        response = self.client.post(reverse('forgot_password'), {'email': 'testuser@test.com'})
        self.assertRedirects(response, reverse('reset_password'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('بازیابی رمز عبور', mail.outbox[0].subject)
        self.assertTrue(PasswordResetCode.objects.filter(user=self.user).exists())

    def test_bad_forgot_password_post(self):
        response = self.client.post(reverse('forgot_password'), {'email': 'wrongemail@test.com'})
        self.assertRedirects(response, reverse('forgot_password'))
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(PasswordResetCode.objects.exists())

class ResetPasswordViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com', password='password')
        self.reset_code = PasswordResetCode.objects.create(user=self.user)
        # self.client.session['reset_user_id'] = self.user.id
        # self.client.session.save()

    def test_reset_password_get(self):
        response = self.client.get(reverse('reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'login/reset_password.html')
        self.assertIsInstance(response.context['form'], ResetPasswordForm)

    # def test_ok_reset_password_post(self):
    #     response = self.client.post(reverse('reset_password'), {'code': self.reset_code.code, 'new_password':'newpassword', 'confirm_new_password': 'newpassword'},)
    #     self.assertRedirects(response, reverse('login'))
    #     self.user.refresh_from_db()
    #     self.assertTrue(check_password('newpassword',self.user.password))
    #     self.assertFalse(PasswordResetCode.objects.filter(user=self.user).exists())

    def test_reset_password_post_wrong_code(self):
        response = self.client.post(reverse('reset_password'), {'code': 'wrongcode', 'new_password': 'newpassword', 'confirm_new_password': 'newpassword'})
        self.assertTemplateUsed(response,'login/reset_password.html')
        self.user.refresh_from_db()
        self.assertFalse(check_password('newpassword',self.user.password))

class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', first_name="test", last_name='test', password='password', email='testuser@test.com')
        self.client.login(username='testuser', password='password')

    def test_patient_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)