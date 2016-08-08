from django.http import HttpResponse
from . import constants as const
import sys
import requests
import xml.etree.ElementTree as ET
import json
from nseapis import NSE

#from suds.client import Client

#def index(request):
#    response = '<?xml version="1.0" encoding="utf-8"?>'
#    response += '<response><status>False</status>'
#    response += '<response><message>Not allowed</message>'
#    response += '<response>'
#    return response


def create_nse_customer(request):
    nse = NSE()    
    resJson = nse.createCustomer()
    
    content_type = 'application/json'
    response = HttpResponse( json.dumps(resJson), content_type=content_type, status=200)
    return response

def get_customer_iin(request):
    nse = NSE()    
    resJson = nse.getIIN()

    content_type = 'application/json'
    response = HttpResponse( json.dumps(resJson), content_type=content_type, status=200)
    return response

def get_customer_iin_details(request):
    nse = NSE()    
    resJson = nse.getIINDetails()

    content_type = 'application/json'
    response = HttpResponse( json.dumps(resJson), content_type=content_type, status=200)
    return response
    
def register_kyc(request):
    nse = NSE()
    resJson = nse.registerKYC()

    content_type = 'application/xml'
    response = HttpResponse( resJson, content_type=content_type, status=200)
    return response

def txn_purchase(request):
    nse = NSE()
    resJson = nse.txnPurchase()

    content_type = 'application/xml'
    response = HttpResponse( resJson, content_type=content_type, status=200)
    return response

def txn_redeem(request):
    nse = NSE()    
    resJson = nse.txnRedeem()

    content_type = 'application/json'
    response = HttpResponse( json.dumps(resJson), content_type=content_type, status=200)
    return response

def txn_switch(request):
    nse = NSE()
    resJson = nse.txnSwitch()

    content_type = 'application/json'
    response = HttpResponse( json.dumps(resJson), content_type=content_type, status=200)
    return response