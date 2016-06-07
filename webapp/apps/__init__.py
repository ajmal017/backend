from random import randint

"""

Place to store common function across all the modules and any init script for apps
"""
import string
import random

def generate_error_message(errors):
    """
    :param errors:
    :return: Returns a string used to send directly as error message.
    """
    error_message = ""
    for key, value in errors.items():
        error_message = key.replace("_", " ").title() + " : " + error_message + " " + str(" ".join(value)) + ", "
    return error_message[:-2]


def random_with_N_digits(n):
    """
    :param n: the length of random number length
    :return: random number of length n
    """
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def code_generator(size, chars=string.ascii_uppercase + string.digits):
    """

    :param size:
    :param chars:
    :return: a random string with caps alphabet and numeric fields
    """
    return ''.join(random.choice(chars) for _ in range(size))
