"""
All positive test cases are covered
Serializer's field which are required are left
"""
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APISimpleTestCase

from profiles.models import User
from core.views import AssessAnswer,DashboardVersionTwo,EducationGoalEstimate,RetirementGoalEstimate,PropertyGoalEstimate,AutomobileGoalEstimate,VacationGoalEstimate
from core import models,views
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
        request = self.factory.get(reverse('api_urls:core_urls:answers-add', kwargs={"type": type}),
                                    data=json.dumps(data), content_type="application/json")
        force_authenticate(request,  user=self.user)
        response = view(request, type)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status_code'], 200)

  
class DashboardVersionTwoTest(APISimpleTestCase):
    allow_database_queries = True
    def test_dashboard(self):
        factory = APIRequestFactory()
        view = views.DashboardVersionTwo.as_view()
        data={}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls:core_urls:dashboard-v2'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class EducationGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.EducationGoalEstimate.as_view()
        data = {"term":11,"location":"op1","field":"op4","amount_saved":500000}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:education-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class RetirementGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.RetirementGoalEstimate.as_view()
        data = {"monthly_income":100000,"monthly_expense":50000,"amount_saved":500000,"current_age":36,"retirement_age":60}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:retirement-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class PropertyGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.PropertyGoalEstimate.as_view()
        data = {"term":6,"current_price":20000000,"prop_of_purchase_cost":30,"amount_saved":2500000}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:property-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class AutomobileGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.AutomobileGoalEstimate.as_view()
        data = {"term":6,"current_price":20000000,"prop_of_purchase_cost":30,"amount_saved":2500000}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:automobile-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)

class VacationGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.VacationGoalEstimate.as_view()
        data = {"term":3,"number_of_members":4,"number_of_days":6,"location":"op2","amount_saved":50000}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:vacation-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
class WeddingGoalEstimate_Test(APISimpleTestCase):
    allow_database_queries = True
    def test(self):
        factory = APIRequestFactory()
        view = views.WeddingGoalEstimate.as_view()
        data = {"term":7,"expected_people":200,"sharing_percenatge":100,"location":"op2","amount_saved":300000}
        user = User.objects.get(email='jp@gmail.com')
        request = factory.get(settings.BASE_URL+reverse('api_urls_v3:core_urls:wedding-goal-estimate'),data=data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)

