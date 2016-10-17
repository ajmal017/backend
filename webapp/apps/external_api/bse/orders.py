from django.conf import settings

from webapp.apps.external_api import constants

from suds.client import Client as suds_client
from suds.plugin import MessagePlugin
from suds.bindings import binding
from suds.sax.element import Element

import logging
import datetime
import calendar


 
    
def getPassword(bulk_orders, user_id='456801', password='123456#', passkey="cat123"):
        
    try:
        action = "http://bsestarmf.in/MFOrderEntry/getPassword"
        headers = {'SOAPAction': action, 'Content-Type' : 'application/soap+xml; charset="UTF-8"', }
        wsdl_url = constants.BSE_ORDER_WSDL
        #wsdl_url = "http://bsestarmf.in/MFOrderEntry/MFOrder.svc?wsdl"
        client = suds_client(wsdl_url, plugins=[], headers=headers)
        wsa_ns = ('wsa', 'http://www.w3.org/2005/08/addressing')
        message_header = Element('To', ns=wsa_ns).setText('http://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc')
        message_header1 = Element('Action', ns=wsa_ns).setText(action)
        header_list = [message_header, message_header1]
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        client.set_options(soapheaders=header_list, prettyxml=True)   
        
        result = client.service.getPassword(user_id, password, passkey)
    except Exception as e:
        result =  None
        
    if result is not None:
        
        token = result.split("|")
        return orderEntry(token[1],bulk_orders)

    else:
        return "Unable to get password"
    
def orderEntry(token_key,bulk_orders):
           
    try:
        
        action = "http://bsestarmf.in/MFOrderEntry/orderEntryParam"
        headers = {'SOAPAction': action, 'Content-Type' : 'application/soap+xml; charset="UTF-8"', }
        wsdl_url = constants.BSE_ORDER_WSDL
        #wsdl_url = "http://bsestarmf.in/MFOrderEntry/MFOrder.svc?wsdl"
        client = suds_client(wsdl_url, plugins=[], headers=headers)
        wsa_ns = ('wsa', 'http://www.w3.org/2005/08/addressing')
        message_header = Element('To', ns=wsa_ns).setText('http://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc')
        message_header1 = Element('Action', ns=wsa_ns).setText(action)
        header_list = [message_header, message_header1]
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        client.set_options(soapheaders=header_list, prettyxml=True)
        
        date = datetime.datetime.utcnow()
        timestamp = calendar.timegm(date.timetuple())
        
        TransCode = bulk_orders['TransCode']
        TransNo = timestamp
        OrderId = bulk_orders['OrderId']
        UserID = bulk_orders['UserID']
        MemberId = bulk_orders['MemberId']
        client_code = bulk_orders['Client_Code']
        scheme_code = bulk_orders['SCHEME_CODE']
        buy_sell = bulk_orders['Purchase_Redeem']
        BuySellType = bulk_orders['Buy_Sell_Type']
        DPTxn = bulk_orders['DPTxn']
        OrderVal = bulk_orders['Order_Val_AMOUNT']
        Qty = bulk_orders['Qty']
        AllRedeem = bulk_orders['AllRedeem']
        FolioNo = bulk_orders['Folio_No']
        Remarks = bulk_orders['Remarks']
        KYCStatus = bulk_orders['KYC_Flag_Char']
        RefNo = bulk_orders['REF_NO']
        SubBrCode = bulk_orders['Sub_Broker_ARN_Code']
        EUIN = bulk_orders['EUIN_Number']
        EUINVal = bulk_orders['EUIN_Declaration']
        MinRedeem = bulk_orders['MIN_redemption_flag']
        DPC = bulk_orders['DPC_Flag']
        IPAdd = bulk_orders['IPAdd']
        Password = token_key
        PassKey = bulk_orders['PassKey']
        Parma1 = bulk_orders['Parma1']
        Parma2 = bulk_orders['Parma2']
        Parma3 = bulk_orders['Parma3']
              

        result = client.service.orderEntryParam(TransCode,TransNo,OrderId,UserID,MemberId,client_code,scheme_code,
                                                buy_sell,BuySellType,DPTxn,OrderVal,Qty,AllRedeem,FolioNo,Remarks,
                                                KYCStatus,RefNo,SubBrCode,EUIN,EUINVal,MinRedeem,DPC,IPAdd,Password,
                                                PassKey,Parma1,Parma2,Parma3)
                                                
    except:
        result = None   
    if result is not None:
        return result
    else:
        return "Failed to post order"

