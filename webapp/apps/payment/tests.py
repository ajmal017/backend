"""
All positive test cases are covered
Serializer's field which are required are left
"""
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from payment import models,views
from django.conf import settings
import json



class TransactionString_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.TransactionString.as_view()
        data={"txn_amount":30000,"web":True}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:payment_urls:get-checksum'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status_code"],200)
