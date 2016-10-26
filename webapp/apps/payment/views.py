from django.db import transaction, IntegrityError

from rest_framework.views import APIView
from django.views.generic import View
from rest_framework import status
from rest_framework import permissions

from . import models, serailizers, constants, utils
from api import utils as api_utils
from webapp.apps import code_generator
from profiles import utils as profile_utils
from core import utils as core_utils
from django.http import HttpResponse

import logging

import sys,traceback


class TransactionString(APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        
        print("Yes here I m ")
        # if profile_utils.check_if_all_set(request.user) and request.user.investorinfo.kra_verified:
        bank_name = request.user.investorbankdetails.ifsc_code.name
        product_id_array = constants.bank_product_id_map.get(bank_name, None)
        if product_id_array is not None:
            txt_bank_id, product_id = product_id_array[0], product_id_array[1]
            if txt_bank_id == "" or product_id == "":
                return api_utils.response({"message" : constants.UNAVAILABE_BANK}, status.HTTP_404_NOT_FOUND,
                                          constants.UNAVAILABE_BANK)
        else:
            return api_utils.response({"message" : constants.UNAVAILABE_BANK}, status.HTTP_404_NOT_FOUND,
                                      constants.UNAVAILABE_BANK)
        serializer = serailizers.TransactionSerializer(data=request.query_params)
        if serializer.is_valid():
            # txt_bank_id = request.query_params.get('txt_bank_id')
            # product_id = request.query_params.get('product_id')
            kwargs = {"txn_amount": request.query_params.get('txn_amount'),
                      "txt_bank_id": txt_bank_id,
                      "product_id": product_id,
                      "additional_info_1": code_generator(40),
                      "additional_info_3": request.user.finaskus_id,
                      "customer_id": code_generator(7),
                      "user_id": request.user.id,}
            billdesk = models.Transaction.objects.create(**kwargs)
            logger = logging.getLogger('django.info')
            logger.info(billdesk.url_hashed())
            return api_utils.response(billdesk.url_hashed())
        return api_utils.response(serializer.errors, status.HTTP_404_NOT_FOUND, constants.MALFORMED_REQUEST)
        # else:
        #     return api_utils.response({"message": constants.USER_CANNOT_INVEST}, status.HTTP_404_NOT_FOUND,
        #                               constants.USER_CANNOT_INVEST)


class Pay(APIView):
    """
    API to return funds in a category of user and funds not in category of user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        Bypass view to make order details before payment is made

        """
        bank_name = request.user.investorbankdetails.ifsc_code.name
        txt_bank_id = 'XXX'
        product_id = bank_name 
        product_id_array = constants.bank_product_id_map.get(bank_name, None)
        if product_id_array is not None:
            txt_bank_id, product_id = product_id_array[0], product_id_array[1]

        serializer = serailizers.TransactionSerializer(data=request.query_params)
        if serializer.is_valid():
            logger = logging.getLogger('django.info')
            try:
                with transaction.atomic():
                    kwargs = {"txn_amount":  request.query_params.get('txn_amount'),
                              "txt_bank_id": txt_bank_id,
                              "product_id": product_id,
                              "additional_info_1": code_generator(40),
                              "additional_info_3": request.user.finaskus_id,
                              "customer_id": code_generator(7),
                              "user_id": request.user.id,}
                    
                    billdesk = models.Transaction.objects.create(**kwargs)
                    core_utils.convert_to_investor(billdesk)
                    return api_utils.response({"message":"success"})
            except IntegrityError as e:
                logger.info("Integrity Error creating order: " + str(e))
                return api_utils.response({"message": "failure"}, status.HTTP_404_NOT_FOUND,
                                          constants.ORDER_CREATION_FAILED)
            except Exception as e:
                logger.info("Error creating order: " + str(e))
                return api_utils.response({"message": "failure"}, status.HTTP_404_NOT_FOUND,
                                          constants.ORDER_CREATION_FAILED)
                
        return api_utils.response(serializer.errors, status.HTTP_404_NOT_FOUND, constants.MALFORMED_REQUEST)
    


class BilldeskInformation(View):
    """

    """
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        if request.user.is_superuser:
            try:
                billdesk = models.Transaction.objects.get(id=request.GET.get('transaction_id'))
                print("hello")
            except models.Transaction.DoesNotExist:
                billdesk = None
        
            bank_name = billdesk.user.investorbankdetails.ifsc_code.name
            product_id_array = constants.bank_product_id_map.get(bank_name, None)
            if product_id_array is not None:
                txt_bank_id, product_id = product_id_array[0], product_id_array[1]
                if txt_bank_id == "" or product_id == "":
                    return HttpResponse({"message" : constants.UNAVAILABE_BANK}, status.HTTP_404_NOT_FOUND,
                                              constants.UNAVAILABE_BANK)
            else:
                return HttpResponse({"message" : constants.UNAVAILABE_BANK}, status.HTTP_404_NOT_FOUND,
                                          constants.UNAVAILABE_BANK)
            
            print(billdesk.merchant_id)
            
            request_type="0122"
            parts = [request_type,billdesk.merchant_id,billdesk.customer_id,billdesk.additional_info_8.strftime("%Y%m%d%H%M%S"),billdesk.url_hashed()]  
            msg = "|".join(parts)
            
            logger = logging.getLogger('django.info')
            logger.info(msg)
            return HttpResponse(msg)
        else:
            return HttpResponse("Not authenticated user")