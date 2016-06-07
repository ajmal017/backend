"""
All positive test cases are covered
Serializer's field which are required are left
"""
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from core.views import AssessQuestion, AssessAnswer, RiskProfile, Question
from core import models

import json

class RiskProfileTests(APISimpleTestCase):

    allow_database_queries = True

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user, created = User.objects.get_or_create(email='username@email.com', password='password')

    def test_1001_get_risk_profile(self):
        """
        Ensure RiskProfile get is working and authenticated user is not required
        """
        view = RiskProfile.as_view()
        request = self.factory.get(reverse('api_urls:core_urls:risk-profile'))
        # force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status_code'], 200)

    def test_1002_get_assess_questions(self):
        """
        Ensure Assess Get api is working and authenticated user is not required
        """
        view = AssessQuestion.as_view()
        request = self.factory.get(reverse('api_urls:core_urls:assess-questions-list'))
        # force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status_code'], 200)

    def test_1003_get_questions_unauthenticated(self):
        """
        Ensure only authenticated user can access question-list apis
        """
        view = Question.as_view()
        type = "plan"
        request = self.factory.get(reverse('api_urls:core_urls:questions-list', kwargs={"type": type}))
        # force_authenticate(request, user=self.user)
        response = view(request, type)
        self.assertEqual(response.status_code, 401)

    def test_1004_get_questions(self):
        """
        Ensure get questions are working only for authenticated user
        """
        view = Question.as_view()
        for type in ["plan", "tax", "retirement", "property", "education", "event", "wedding"]:
            request = self.factory.get(reverse('api_urls:core_urls:questions-list', kwargs={"type": type}))
            force_authenticate(request, user=self.user)
            response = view(request, type)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['status_code'], 200)


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

    def test_1002_check_answer(self):
        """
        Ensure get questions are working only for authenticated user
        """
        view = Question.as_view()
        type = "plan"
        request = self.factory.get(reverse('api_urls:core_urls:questions-list', kwargs={"type": type}))
        force_authenticate(request, user=self.user)
        response = view(request, type)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response'][0]['user_answer'], [{'metadata': None, 'answer': '2'}])
        self.assertEqual(response.data['response'][1]['user_answer'], [{'metadata': None, 'answer': 'nice work'}])
        self.assertEqual(response.data['response'][2]['user_answer'], [{'metadata': {'order': '1'}, 'answer': 'wedding 11'}])



