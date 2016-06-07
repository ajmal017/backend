from django.db import models

from rest_framework import serializers
from rest_framework import status

from api import utils as api_utils


class QuestionManager(models.Manager):
    """
    Manager for querying on Question model
    """
    def get_questions_by_id(self, id):
        """
        Get Question BY Id
        :param id:
        """
        try:
            return self.get(pk=int(id))
        except Exception as error:
            raise serializers.ValidationError({'message': 'Question Not Found'})

    def get_questions_by_category(self, category):
        """
        :param category:
        :return:
        """
        return self.filter(question_for=category).order_by('order')

    def get_questions_by_user(self, user):
        """
        :param user:
        Get Question answered by user
        """
        return self.filter(questions__user=user)


class AnswerManager(models.Manager):
    """
    Manager for querying on Answer model
    """
    def get_answers_by_user(self, user, question_list):
        """
        :param user:
        :param question_list:
        :return:
        """
        return self.filter(user=user, question__in=question_list)


class OptionManager(models.Manager):
    """
    Manager for querying on Option Model
    """
    def get_option_by_id(self, id):
        """
        :param id:
        :return option wrt id if found else raise validation error:
        """
        try:
            return self.get(id=id)
        except Exception as error:
            raise serializers.ValidationError({'message': 'Option Not Found'})


class FundManager(models.Manager):
    """
    Manager for querying on Question model
    """
    def get_fund_by_id(self, id):
        """
        Get Fund BY Id
        :param id: the id of fund
        """
        try:
            return self.get(id=int(id))
        except Exception as e:
            # TODO we need to raise a validation error and make sure it follows the standard of our api return code
            return api_utils.response({"message": "Fund not found"}, status.HTTP_400_BAD_REQUEST, "Fund not found")
