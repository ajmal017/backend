from . import models

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


def get_valid_start_date(fund_id, send_date=datetime.now()):
    """
    generates valid start date for a prticular fund
    :param fund_id: id of a particular fund
    :param send_date: base date to be used as base date for finding valid start date
    :return: next valid start date
    """
    sip_dates = models.Fund.objects.get(id=fund_id).sip_dates
    sip_dates.sort()
    next_month = (send_date + timedelta(30))
    day = next_month.day
    if day > sip_dates[-1]:
        next_month += timedelta(30)
        next_month = next_month.replace(day=sip_dates[0])
        return next_month
    modified_day = next(date[1] for date in enumerate(sip_dates) if date[1] >= day)
    next_month = next_month.replace(day=modified_day)
    return next_month
