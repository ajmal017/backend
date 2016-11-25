from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

def roundTo100(amount1, amount2):
    amount1_remainder = amount1%100
    if amount1_remainder < 50:
        amount1 -= amount1_remainder
        amount2 += amount1_remainder
    else:
        amount1 += (100 - amount1_remainder)
        amount2 -= (100 - amount1_remainder)
    return amount1, amount2

def calculate_time_delta(date1, date2):
    time_delta = relativedelta(date2, date1).months
    date1 += relativedelta(months=time_delta)
    time_delta += relativedelta(date2, date1).years * 12
    
    return time_delta
