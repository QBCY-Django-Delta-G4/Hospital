from django.test import TestCase
from django.contrib.auth.models import User
from management.models import Doctor, Patient, Comment, Specialization


class CommentTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.specializations = Specialization.objects.create(title="جراح پلاستیک")
        self.doctor = Doctor.objects.create(
            first_name='محمد',
            last_name='کمالی',
            phone='1234567890',
            specializations=self.specializations,
            clinic_address='آدرس مطب',
            license_number=123456,
            biography='بیوگرافی دکتر',
            visit_cost=2000.000
        )

        self.patient = Patient.objects.create(
            user=self.user,
            balance=1000.456,
            phone='0987654321'
        )

        self.comment = Comment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            description='تست هستند',
            is_visited=True
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.doctor, self.doctor)
        self.assertEqual(self.comment.patient, self.patient)
        self.assertEqual(self.comment.description, 'تست هستند')
        self.assertTrue(self.comment.is_visited)
        self.assertFalse(self.comment.is_deleted)
        self.assertTrue(self.comment.created_at <= self.comment.updated)

    def test_default_values(self):
        comment = Comment.objects.create(
            doctor=self.doctor,
            description='تست کامنت بدون patient'
        )

        self.assertTrue(comment.active)
        self.assertFalse(comment.is_visited)
        self.assertFalse(comment.is_deleted)

    def test_str_method(self):
        expected_str = f"{self.patient.user.username} to {self.doctor.first_name}"
        self.assertEqual(str(self.comment), expected_str)


        comment_without_patient = Comment.objects.create(
            doctor=self.doctor,
            description='تست کامنت بدون patient'
        )
        expected_str_without_patient = f"unAuthorized to {self.doctor.first_name}"
        self.assertEqual(str(comment_without_patient), expected_str_without_patient)