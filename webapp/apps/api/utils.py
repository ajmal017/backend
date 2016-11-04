from rest_framework.response import Response
from rest_framework import status

import string
import random
import time


def response(data, code=status.HTTP_200_OK, error="",headers=None):
    """
    Overrides rest_framework response

    :param data: data to be send in response
    :param code: response status code(default has been set to 200)
    :param error: error message(if any, not compulsory)

    """
    res = {"status_code": code, "error": error, "response": data}
    return Response(data=res, status=status.HTTP_200_OK,headers=headers)


def gen_hash(seed):
    """
    :param seed: seed for random generation
    :return: hash key
    """
    base = string.ascii_letters+string.digits  # Output hash base: all alphabets and digits
    random.seed(seed)  # Input string as the random seed
    hash_value = ""
    for i in range(15):
        # Generate a 15-character hash by randomly select characters from base
        hash_value += random.choice(base)
    return hash_value


def expires():
    """
    :return: a UNIX style timestamp representing 5 minutes from now
    """
    return int(random.randint(1, 9969)*(time.time()+300))


def create_error_message(error_dict):
    """
    Changes a dict of errors into a string
    :param error_dict:a dictionary of errors
    :return:a string made of errors
    """
    error_string = ''
    for error in error_dict:
        error_string += error_dict[error] + ". "
    return error_string


def age_calculator(answers, portfolio):
    """
    returns the differenc between current age and retirement age
    :params answers
    :params portfolio
    """
    difference_in_age = None
    type_of_age_name = ['current_age', 'retirement_age']
    current_age = answers.filter(question__question_id__in=type_of_age_name, portfolio=portfolio)
    if len(current_age) == 2:
        difference_in_age = abs(int(current_age[0].text) - int(current_age[1].text))
    return difference_in_age
