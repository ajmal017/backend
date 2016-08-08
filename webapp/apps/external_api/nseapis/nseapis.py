from django.http import HttpResponse
from django.db import migrations, models
from django.http import HttpResponse
from . import constants as const
import sys
import requests
import xml.etree.ElementTree as ET
import json

class NSE:
    
    """
    NSE APIs Facade
    """
    url = ''
    
    def __init__( self ):
        print "Initiating NSE APIs..."
        NSE.url = const.NSE_NMF_API_URL
    
    def createCustomer(self):
       
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        resFile = requests.post(NSE.url+const.NMF_METHOD_CREATECUSTOMER, data=const.REQUEST_CREATECUSTOMER, headers=headers)
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

        resJson = {}
        resJson['message']  = retMessage[0].text  
        if retStatus[0].text == 0:
            resJson['status']   = True            
        else :
            resJson['status']   = False
        
        return resJson

    def getIIN( self ):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        
        resFile = requests.post(NSE.url+const.NMF_METHOD_GETIIN, data=const.REQUEST_GETIIN, headers=headers)        
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

        resJson = {}
        resJson['message']  = retMessage[0].text
        if retStatus[0].text == 0:
            resJson['status']   = True
        else :
            resJson['status']   = False

        return resJson
    
    def getIINDetails( self ):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        
        resFile = requests.post(NSE.url+const.NMF_METHOD_GETIIN, data=const.REQUEST_GETIIN, headers=headers)        
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

        resJson = {}
        resJson['message']  = retMessage[0].text
        if retStatus[0].text == 0:
            resJson['status']   = True
        else :
            resJson['status']   = False

        return resJson
    
    def registerKYC(self):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        resFile = requests.post(NSE.url+const.NMF_METHOD_FATCAKYCUBOREG, data=const.REQUEST_FATCAKYCUBOREG, headers=headers)
        root = ET.fromstring(resFile.content)

#        retStatus  = root.findall(".//service_return_code")
#        retMessage = root.findall(".//return_msg")
#
#        resJson = {}
#        resJson['message']  = retMessage[0].text
#        if retStatus[0].text == 0:
#            resJson['status']   = True
#        else :
#            resJson['status']   = False
        
        return resFile
    
    def txnPurchase(self):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        resFile = requests.post(NSE.url+const.NMF_METHOD_PURCHASETRXN, data=const.REQUEST_TXN_PURCHASE, headers=headers)
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

#        resJson = {}
#        resJson['message']  = retMessage[0].text
#        if retStatus[0].text == 0:
#            resJson['status']   = True
#        else :
#            resJson['status']   = False
        
        return resFile
    
    def txnRedeem(self):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        resFile = requests.post(NSE.url+const.NMF_METHOD_REDEEMTRXN, data=const.REQUEST_TXN_REDEEM, headers=headers)
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

        resJson = {}
        resJson['message']  = retMessage[0].text
        if retStatus[0].text == 0:
            resJson['status']   = True
        else :
            resJson['status']   = False
        
        return resJson
    
    def txnSwitch(self):
        headers = {'content-type': 'application/xml', 'accept': 'application/xml' }
        resFile = requests.post(NSE.url+const.NMF_METHOD_SWITCHTRXN, data=const.REQUEST_TXN_SWITCH, headers=headers)
        root = ET.fromstring(resFile.content)

        retStatus  = root.findall(".//service_return_code")
        retMessage = root.findall(".//return_msg")

        resJson = {}
        resJson['message']  = retMessage[0].text
        if retStatus[0].text == 0:
            resJson['status']   = True
        else :
            resJson['status']   = False
        
        return resJson