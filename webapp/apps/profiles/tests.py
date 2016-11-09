from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from profiles.views import UserInfo, Register, Login, ResetPassword
from core.views import AssessAnswer,AssessAnswer_v3, AssessAnswer_Unregistered_User_v3
from profiles import models
from django.conf import settings



class GetProfileTests(APISimpleTestCase):

    allow_database_queries = True

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user, created = User.objects.get_or_create(email='username@email.com', password='password')

    def test_1001_get_profile(self):
        """
        Ensure UserInfo Profile get is working and authenticated user is required
        """
        view = UserInfo.as_view()
        request = self.factory.get(reverse('api_urls:profiles_urls:user-info'))
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status_code'], 200)


# class PostTest(APISimpleTestCase):
#
#     allow_database_queries = True
#
#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.user, created = User.objects.get_or_create(email='username@email.com', password='password')
#
#     # def test_1001_post_profile(self):
#     #
#     #     view = ResetPassword.as_view()
#     #     request = self.factory.post(reverse('api_urls:profiles_urls:reset-password'))
#     #     # force_authenticate(request, user=self.user)
#     #     response = view(request)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.data['status_code'], 404)
#     #
#     # def test_1002_post_profile(self):
#     #
#     #     view = Register.as_view()
#     #     request = self.factory.post(reverse('api_urls:profiles_urls:register-user'))
#     #     # force_authenticate(request, user=self.user)
#     #     response = view(request)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.data['status_code'], 404)
#
#
#

class RegisterTest(APISimpleTestCase):
    allow_database_queries = True
    def test_register(self):
        factory = APIRequestFactory()
        view = Register.as_view()
        data={"email":"test@email.com","username":"test@email.com","password":"password@1234","phone_number":"9000000000"}
        request = factory.post(settings.BASE_URL+reverse('api_urls:profiles_urls:register-user'),data=data)
        #force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class LoginTest(APISimpleTestCase):
    allow_database_queries = True
    def test_login(self):
        factory = APIRequestFactory()
        view = Login.as_view()
        data={"username":"jp@gmail.com","password":"jinesh@1234"}
        request = factory.post(settings.BASE_URL+reverse('api_urls:profiles_urls:login-user'),data=data)
        #force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        
class AssessAnswers(APISimpleTestCase):
    allow_database_queries = True
    def test_register(self):
        factory = APIRequestFactory()
        view = AssessAnswer.as_view()
        data={'A2': 'op2', 'A6': 'op2', 'A5': 'op2', 'A3': 'op2', 'A4': 'op2', 'A1': '35'}
        user = models.User.objects.get(email='jp@gmail.com')
        request = factory.post(settings.BASE_URL+reverse('api_urls:core_urls:assess-new-answers-add'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class AssessAnswers_v3(APISimpleTestCase):
    allow_database_queries = True
    def test_register(self):
        factory = APIRequestFactory()
        view = AssessAnswer_v3.as_view()
        data={'A4': 'op2', 'A1': '35','A7': 'op2', 'A8': 'op2', 'A9': 'op2', 'A17': 'op2','A18': 'op2','A19': 'op2'}
        user = models.User.objects.get(email='jp@gmail.com')
        request = factory.post(settings.BASE_URL+reverse('api_urls_v3:core_urls:assess-new-answers-add'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        
        


