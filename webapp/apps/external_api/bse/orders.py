from django.conf import settings

from webapp.apps.external_api import constants

from suds.client import Client as suds_client
from suds.plugin import MessagePlugin
from suds.bindings import binding
from suds.sax.element import Element

import logging


logger = logging.getLogger("default")


class ValidSoapResponse(MessagePlugin):
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

class Order(object):

    def __init__(self,bulk_orders):
        action = "http://bsestarmf.in/MFOrderEntry/getPassword"
        headers = {'SOAPAction': action, 'Content-Type' : 'application/soap+xml; charset="UTF-8"', }
        #wsdl_url = constants.BSE_ORDER_WSDL
        wsdl_url = "http://bsestarmf.in/MFOrderEntry/MFOrder.svc?wsdl"
        # plugin = ValidSoapResponse()
        self.client = suds_client(wsdl_url, plugins=[], headers=headers)
        wsa_nsa = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        wsa_ns = ('wsa', 'http://www.w3.org/2005/08/addressing')
        wsa_nsb = ('ns1', "http://www.w3.org/2003/05/soap-envelope")
        message_header = Element('To', ns=wsa_ns).setText('http://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc')
        message_header1 = Element('Action', ns=wsa_ns).setText(action)
        header_list = [message_header, message_header1]
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        self.client.set_options(soapheaders=header_list, prettyxml=True)
        
        self.gp(bulk_orders)
        

    def all_methods(self):
        list_of_methods = [method for method in self.client.wsdl.services[0].ports[0].methods]
        print(list_of_methods)

    def gp(self, bulk_orders, user_id, password, passkey="cat123"):
        """
        # crete theTransaction objects as o = Order(constants.BSE_ORDER_GET_PASSWORD_URL)
        :param user_id:
        :param password:
        :param passkey:
        :return:
        """
        try:
            result = self.client.service.getPassword(user_id, password, passkey)
        except Exception as e:
            result =  None
        
        if result is not None:
            token = result.split("|")
            self.orderEntry(token[1],bulk_orders)
        else:
            return "Unable to get password"
         
    
    
    """
     Place an order
    """
    def orderEntry(self,token_key,bulk_orders):
        
        print(bulk_orders['scheme_code'])
        
        try:
            result = self.client.service.orderEntryParam()
        except:
            result = None
        
        if result is not None:
            return result
        else:
            return "Failed to post order"
        