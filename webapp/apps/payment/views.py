from django.db import transaction, IntegrityError

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions

from . import models, serailizers, constants, utils
from api import utils as api_utils
from webapp.apps import code_generator
from profiles import utils as profile_utils
from core import utils as core_utils
from external_api import helpers as external_api_helpers

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
        active_exchange_vendor = external_api_helpers.get_exchange_vendor_helper().get_active_vendor()
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
            payment_link, error_status = active_exchange_vendor.generate_payment_link(billdesk)
            if payment_link:
                logger.info(payment_link)
                return api_utils.response(payment_link)
            return api_utils.response({"message":error_status}, status.HTTP_428_PRECONDITION_REQUIRED, error_status)
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
        active_exchange_vendor = external_api_helpers.get_exchange_vendor_helper().get_active_vendor()
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
                kwargs = {"txn_amount":  request.query_params.get('txn_amount'),
                          "txt_bank_id": txt_bank_id,
                          "product_id": product_id,
                          "additional_info_1": code_generator(40),
                          "additional_info_3": request.user.finaskus_id,
                          "customer_id": code_generator(7),
                          "user_id": request.user.id,}
                
                billdesk = models.Transaction.objects.create(**kwargs)
                core_utils.convert_to_investor(billdesk, active_exchange_vendor)
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