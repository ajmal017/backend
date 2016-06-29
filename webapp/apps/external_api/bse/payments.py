from django.conf import settings

from webapp.apps.external_api import constants
from webapp.apps import code_generator

from suds.client import Client as suds_client
from suds.plugin import MessagePlugin
from suds.bindings import binding
from suds.sax.element import Element

import logging


logger = logging.getLogger("default")


class ValidSoapResponse(MessagePlugin):
    def marshalled(self, context):
        #modify this line to reliably find the "recordReferences" element
        # context.envelope[1].setPrefix('ns1')
        context.envelope[1].setPrefix('ns0')

    def sending(self, context):
        xml_req = str(context.envelope)

    def received(self, context):
        xml_res = context.reply
        answer = context.reply

        answerDecoded = answer.decode()
        header_split = answerDecoded.split('<soap:Envelope')
        header_split_msg = '<soap:Envelope' + header_split[1]

        footer_split = header_split_msg.split('</soap:Envelope>')
        replyFinal = footer_split[0] + '</soap:Envelope>'

        replyFinalDecoded = replyFinal.encode()
        context.reply = replyFinalDecoded


class Payment(object):

    def __init__(self, action):
        headers = {'SOAPAction': action, 'Content-Type' : 'application/soap+xml; charset="UTF-8"', }
        wsdl_url = 'http://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc?wsdl'
        # plugin = ValidSoapResponse()
        self.client = suds_client(wsdl_url, plugins=[], headers=headers)
        wsa_ns = ('wsa', 'http://www.w3.org/2005/08/addressing')
        # wsa_nsa = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        wsa_nsb = ('ns1', "http://www.w3.org/2003/05/soap-envelope")
        message_header = Element('To', ns=wsa_ns).setText(constants.TO_URL)
        message_header1 = Element('Action', ns=wsa_ns).setText(action)
        header_list = [message_header, message_header1]
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        self.client.set_options(soapheaders=header_list, prettyxml=True)

    def all_methods(self):
        """
        :return: Prints all the methods of the wsdl file
        """
        list_of_methods = [method for method in self.client.wsdl.services[0].ports[0].methods]
        print(list_of_methods)

    def get_encrypted_password(self, user_id, member_id,  password, passkey):
        """
        # create theTransaction objects as p = Payment(constants.GET_PASSWORD_URL)
        :param user_id:
        :param member_id:
        :param password:
        :param passkey:
        :return: an array with status code and encrypted password
        """
        try:
            self.client.set_options(location=constants.TO_URL)
            result = self.client.service.getPassword(member_id, user_id, password, passkey)
        except Exception as e:
            print(e)
            return None
        return result.split("|")


# transaction = Payment(constants.GET_PASSWORD_URL)
# passkey = code_generator(8)
# transaction.get_encrypted_password(settings.BSE_DEMO_USERID, settings.BSE_DEMO_MEMBERID, settings.BSE_DEMO_PASSWORD, passkey)
