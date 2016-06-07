from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from profiles.views import UserInfo, Register, Login, ResetPassword
from profiles import models

import json


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

