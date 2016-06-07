from django.conf import settings

from .sms_backend import  BaseSmsBackend
from . import models, constants

import requests

MGAGE_USERNAME = getattr(settings, 'MGAGE_USERNAME', '')
MGAGE_PASSWORD = getattr(settings, 'MGAGE_PASSWORD', '')
MGAGE_FROM_NUMBER = getattr(settings, 'MGAGE_FROM_NUMBER', '')
MGAGE_API_URL_SENDSMS = 'http://api.unicel.in/SendSMS/sendmsg.php'


class MGageBackend(BaseSmsBackend):
    """
    A wrapper that manages the MGage SMS Backends
    http://api.unicel.in/SendSMS/sendmsg.php?uname=XXX&pass=XXX&send=91XXXXXXXXXX&dest=91XXXXXXXXXX&msg=XXXX

    """
    # TODO: Add function to check balance ?

    def get_username(self):
        return MGAGE_USERNAME

    def get_password(self):
        return MGAGE_PASSWORD

    def get_from_phone_number(self):
        return MGAGE_FROM_NUMBER

    def send_messages(self, sms_messages):
        """
        Sends one or more SmsMessage objects and returns the number of sms messages sent.
        """
        if not sms_messages:
            return

        num_sent = 0
        for message in sms_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, message):
        """
        A helper method that does the actual sending.
        """
        sms = models.SMS(content=message.get('body'), to=message.get('to'), operator=constants.OPERATOR_MGAGE)
        params = {
          'uname': self.get_username(),
          'pass': self.get_password(),
          'send': self.get_from_phone_number(),
          'dest': message.get('to'),
          'msg': message.get('body')
        }
        if len(message.get('body')) > 159:
            params['concat'] = constants.MGAGE_MESSAGE_CONCAT_TRUE

        response = requests.get(MGAGE_API_URL_SENDSMS, params=params)

        if response.status_code == 200:
            # response text returns mid when 200
            # Example: 2016021915093072610, 2116021915143433760
            sms.mid = response.text
            sms.save()
            return True
        else:
            sms.failure_code = response.status_code
            sms.save()
            if not self.fail_silently:
                raise Exception("Error in sending sms: [" + response.text + "]")
            return False
