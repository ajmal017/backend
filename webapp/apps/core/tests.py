"""
All positive test cases are covered
Serializer's field which are required are left
"""
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from core.views import AssessAnswer, RiskProfile,DashboardVersionTwo
from core import models
from django.conf import settings

import json

class PostTest(APISimpleTestCase):

    allow_database_queries = True

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user, created = User.objects.get_or_create(email='username@email.com', password='password')
        self.question_radio, created = models.Question.objects.get_or_create(question_for='P', type='R', text='This is question radio', order=1)
        self.question_text, created = models.Question.objects.get_or_create(question_for='P', type='T', text='This is question text', order=2)
        self.question_multiple, created = models.Question.objects.get_or_create(question_for='P', type='M', text='This is question multiple', order=3)
        self.option_yes, created=models.Option.objects.get_or_create(question=self.question_radio, text='yes')
        self.option_no, created=models.Option.objects.get_or_create(question=self.question_radio, text='no')

    def test_1001_create_plan_answers(self):
        """
        Ensure we can create a new subcategory object.
        """
        view = AssessAnswer.as_view()
        type = "plan"
        data = {
            "fields":[{"question":self.question_radio.id, "answers":[{"option": self.option_no.id}], "type":"R"},
                      {"question":self.question_text.id, "answers":[{"text": "nice work"}], "type":"T"},
                      {"question":self.question_multiple.id, "answers":[{"text":"wedding 11", "metadata" : {"order":"1"}}], "type":"M"}
                     ]
                }
        request = self.factory.post(reverse('api_urls:core_urls:answers-add', kwargs={"type": type}),
                                    data=json.dumps(data), content_type="application/json")
        force_authenticate(request,  user=self.user)
        response = view(request, type)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status_code'], 200)

  


class DashboardVersionTwoTest(APISimpleTestCase):
    allow_database_queries = True
    def test_dashboard(self):
        factory = APIRequestFactory()
        view = DashboardVersionTwo.as_view()
        data={}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls:core_urls:dashboard-v2'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)

