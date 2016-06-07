from webapp.conf import settings

import bs4
import requests


def get_cvl_password():
    """

    :return:
    """
    get_password_payload = dict(password=settings.CVL_PASSWORD, PassKey=settings.CVL_PASSKEY)
    get_password_response = requests.post(settings.CVL_PASSWORD_URI, data=get_password_payload)
    soup = bs4.BeautifulSoup(get_password_response.text, "html.parser")
    return soup.find('string').string


def get_pancard_status(password, pan_number):
    """

    :return:
    """
    name = None
    get_pan_status_payload = dict(password=password, PassKey=settings.CVL_PASSKEY, userName=settings.CVL_USERID,
                                  PosCode=settings.CVL_POSCODE, panNo=pan_number)
    service_response = requests.post(settings.CVL_PANCARD_URI, data=get_pan_status_payload)
    soup = bs4.BeautifulSoup(service_response.text, "html.parser")
    app_status = soup.find('app_status').string
    name = soup.find('app_name').string
    return app_status, name