
from datetime import datetime, timedelta

def find_right_option(value):
    """
    Helper function to return correct option based on age of user
    :param value: the value of age entered by user
    :return: the option in which the age value falls
    """
    if value <= 25:
        return "op1"
    elif value <= 35:
        return "op2"
    elif value <= 40:
        return "op3"
    elif value <= 45:
        return "op4"
    elif value <= 55:
        return "op5"
    else:
        return "op6"


def percentage(dividend, divisor):
    """
    Calculates percentage rounded to two decimals
    :param dividend: the dividend
    :param divisor: the divisor
    :return: percentage rounded to two digits
    """
    return round(((dividend*100)/divisor), 1)

