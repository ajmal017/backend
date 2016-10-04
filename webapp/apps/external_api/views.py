from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.views.generic import View

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions

from external_api.nse.nsebackend import NseBackend
from payment.models import Transaction
from external_api.nse import constants as nse_contants
from external_api import helpers
from . import investor_info_generation, bse_investor_info_generation, bulk_order_entry, kyc_pdf_generator, \
    xsip_registration, bank_mandate
from core.models import OrderDetail, RedeemDetail, GroupedRedeemDetail
from . import models, constants, serializers, cvl
from api import utils as api_utils
from profiles.utils import is_investable
from profiles import pr_utils

from profiles import models as pr_models
from payment import constants as payment_constant

import time


class VerifiablePincode(APIView):
    """
    Sends the current email verification status of a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:  Sends the current email verification status of a user
        """
        pincode_count = models.VerifiablePincode.objects.filter(
            pincode__pincode__in=[request.data.get('pincode', None)]).count()
        if pincode_count > 0:
            return api_utils.response({"verifiable": True, "message": constants.YES_DOORSTEP_VERIFICATION})
        return api_utils.response({"verifiable": False, "message": constants.NO_DOORSTEP_VERIFICATION})


class BankInfoGet(APIView):
    """
    API to return bank info on basis of IFSC code
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        returns bank details on basis of IFSC code
        :param request:
        :return:
        """
        ifsc_code = request.query_params.get('ifsc_code')
        try:
            bank_detail = models.BankDetails.objects.get(ifsc_code=ifsc_code)
        except models.BankDetails.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.IFSC_CODE_INCORRECT}, status.HTTP_404_NOT_FOUND,
                                      constants.IFSC_CODE_INCORRECT)
        """
            return api_utils.response({constants.MESSAGE: constants.UNSUPPORTED_BANK}, status.HTTP_404_NOT_FOUND,
                                      constants.UNSUPPORTED_BANK)
        """
        serializer = serializers.BankInfoGetSerializer(bank_detail)
        return api_utils.response(serializer.data)

        return api_utils.response({constants.MESSAGE: constants.UNSUPPORTED_BANK}, status.HTTP_404_NOT_FOUND,
                                  constants.UNSUPPORTED_BANK)


class KycApi(APIView):
    """
    gets the status of the pan card
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:  Sends the current PAN status
        """
        password = cvl.get_cvl_password()
        pan_status, name = cvl.get_pancard_status(password, request.data.get('pan_number'))
        new_status = True if pan_status[-2:] == "02" else False
        payload_data = dict(kra_verified=new_status, applicant_name=name, pan_number=request.data.get('pan_number'))
        with transaction.atomic():
            try:
                pr_models.InvestorInfo.objects.update_or_create(user=request.user, defaults=payload_data)
            except IntegrityError:
                return api_utils.response({"message": constants.UNACCEPTABLE_PAN_NUMBER},
                                          status.HTTP_404_NOT_FOUND, constants.UNACCEPTABLE_PAN_NUMBER)
        return api_utils.response({"status": new_status, "name": name})

class BulkRegisterUCC(object):
    def get(self, user_list):
        """
        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pipe file
        """
        exch_backend = helpers.get_backend_instance()
        if exch_backend:
            not_set = []
            for i in user_list:
                user = pr_models.User.objects.get(id=i)
                if not is_investable(user):
                    not_set.append(user.id)
            if len(not_set) > 0:
                return not_set

            return exch_backend.bulk_create_customer(user_list)

class GenerateInvestorPdf(View):
    """
    An api to generate pdf for the pertinent investor.
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private investor file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pdf
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            user = pr_models.User.objects.get(email=request.GET.get('email'))
            if is_investable(user) and user.signature != "":
                output_file = investor_info_generation.investor_info_generator(user.id).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix + constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'application/pdf'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id) + "_" + time.strftime(
                    "%Y%m%d-%H%M%S") + "_investor.pdf"
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.USER_CANNOT_INVEST, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateKycPdf(View):
    """
    An api to generate kyc pdf for the pertinent user.
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private KYC PDF.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated kyc pdf
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            user = pr_models.User.objects.get(email=request.GET.get('email'))
            if is_investable(user) and user.signature != "":
                output_file = kyc_pdf_generator.generate_kyc_pdf(user.id).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix + constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'application/pdf'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id) + '_kyc.pdf'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.USER_KYC_CANNOT_GENERATE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)

    
class GenerateBseOrderPipe(View):
    """
    An api to generate pipe file for bulk order entry
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private Bse order pipe file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pipe file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            order_detail = OrderDetail.objects.get(order_id=request.GET.get('order_id'))
            order_items = order_detail.fund_order_items.all()
            if is_investable(order_detail.user):
                output_file = bulk_order_entry.generate_order_pipe_file(order_detail.user, order_items).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix + constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id) + '_order.txt'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateXsipRegistration(View):
    """
    An api to do XSIP registration.
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private xsip pipe file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pipe file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            order_detail = OrderDetail.objects.get(order_id=request.GET.get('order_id'))
            order_items = order_detail.fund_order_items.all()
            if is_investable(order_detail.user):
                output_file = xsip_registration.generate_user_pipe_file(order_detail.user, order_items).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix + constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id) + '_xip_order.txt'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateBankMandateRegistration(View):
    """
    An api to generate bank mandate.
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private bank mandate pipe file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pipe file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            order_detail = OrderDetail.objects.get(order_id=request.GET.get('order_id'))
            if is_investable(order_detail.user):
                exch_backend = helpers.get_backend_instance()
                if exch_backend:
                    mandate_amount = pr_utils.get_investor_mandate_amount(order_detail.user, order_detail)
                    status, output_file = exch_backend.generate_bank_mandate_registration(order_detail.user.id, mandate_amount)
                    if status == constants.RETURN_CODE_SUCCESS:
                        if output_file:
                            output_file = output_file.split('/')[-1]
                            prefix = 'webapp'
                            my_file_path = prefix + constants.STATIC + output_file
                            my_file = open(my_file_path, "rb")
                            content_type = 'text/plain'
                            response = HttpResponse(my_file, content_type=content_type, status=200)
                            response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id) + '_order.txt'
                            my_file.close()
                            return response  # contains the pipe file of the pertinent user
                        else:
                            return HttpResponse(constants.SUCCESS, status=200)
            # file doesn't exist because investor vault is incomplete.
            return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class NseOrder(View):
    """
    An api to generate bank mandate.
    """

    def get(self, request):
        """

        :param request: user_id of the user and payment type online/offline.
        :return: send the payment link url
        """

        # getiin, if error create customer and then recieve iin and save to db
        # depending on txn type sip/lumpsum make requests for payment link if online

        user_id = request.query_params.get('user_id')
        try:
            user = pr_models.User.objects.get(id=user_id)
            investor_bank = pr_models.InvestorBankDetails.objects.get(user=user)
            if user.vault_locked:
                nse = NseBackend()
                status_code = nse.get_iin(user_id=user_id)
                if status_code == nse_contants.RETURN_CODE_FAILURE:
                    return_code = nse.create_customer(user_id=user_id)
                if investor_bank.sip_check:
                        nse.generate_bank_mandate_registration(user_id=user_id)
                        nse.upload_img(user_id=user_id, image_type="X")  # 'X' for Transaction type of image and 'A' for IIN Form
                status_code = nse.purchase_trxn(user_id=user_id)
                if status_code == nse_contants.RETURN_CODE_SUCCESS:
                    current_transaction = Transaction.get(user_id=user_id, txn_status=0)
                    payment_link = current_transaction.payment_link
                    return api_utils.response({"payment_link": payment_link})
                else:
                    return api_utils.response({constants.MESSAGE: constants.PURCHASE_TXN_FAILED}, status.HTTP_404_NOT_FOUND,
                                              constants.PURCHASE_TXN_FAILED)
            else:
                return api_utils.response({constants.MESSAGE: constants.VAULT_NOT_CLOSED}, status.HTTP_412_PRECONDITION_FAILED,
                                          constants.VAULT_NOT_CLOSED)
        except pr_models.User.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_NOT_FOUND}, status.HTTP_404_NOT_FOUND,
                                      constants.USER_NOT_FOUND)

class UploadAOFTiff(View):
    """
    an api to generate Bse Investor info pdf
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private Bse info Tiff file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated tiff file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            exch_backend = helpers.get_backend_instance()
            if exch_backend:
                user = pr_models.User.objects.get(email=request.GET.get('email'))
                if is_investable(user) and user.signature != "":
                    result = exch_backend.upload_aof_image(user.id)
                    if result == constants.RETURN_CODE_SUCCESS:
                        return HttpResponse(constants.SUCCESS, status=200)
            # file doesn't exist because investor vault is incomplete.
            return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)

class GenerateAOFTiff(View):
    """
    an api to generate Bse Investor info pdf
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private Bse info Tiff file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated tiff file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            exch_backend = helpers.get_backend_instance()
            if exch_backend:
                user = pr_models.User.objects.get(email=request.GET.get('email'))
                if is_investable(user) and user.signature != "":
                    output_file = exch_backend.generate_aof_image(user.id).split('/')[-1]
                    prefix = 'webapp'
                    my_file_path = prefix + constants.STATIC + output_file
                    my_file = open(my_file_path, "rb")
                    content_type = 'image/tiff'
                    download_name = user.id
                    response = HttpResponse(my_file, content_type=content_type, status=200)
                    response['Content-Disposition'] = 'attachment;filename=%s' % download_name + ".tiff"
                    my_file.close()
                    return response  # contains the pdf of the pertinent user
                else:
                    # file doesn't exist because investor vault is incomplete.
                    return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateBseRedeemPipe(View):
    """
    An api to generate pipe file for redeem
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private Bse redeem pipe file.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated pipe file
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            group_redeem_detail = GroupedRedeemDetail.objects.get(id=request.GET.get('group_redeem_id'))
            redeem_items = group_redeem_detail.redeem_details.all()
            if is_investable(group_redeem_detail.user):
                output_file = \
                bulk_order_entry.generate_redeem_pipe_file(group_redeem_detail.user, redeem_items).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix + constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(group_redeem_detail.id) + 'redeem.txt'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateMandatePdf(View):
    """
    An api to generate bank mandate pdf for the pertinent user.
    """

    def get(self, request):
        """
        Only admin user is allowed to access the private mandate PDF.

        :param request: the email_id of the pertinent user is received from this.
        :return: send the generated bank_mandate pdf
        """

        # makes sure that only superuser can access this file.

        if request.user.is_superuser:
            exch_backend = helpers.get_backend_instance()
            if exch_backend:
                user = pr_models.User.objects.get(email=request.GET.get('email'))
                if is_investable(user) and user.signature != "":
                    mandate_amount = pr_utils.get_investor_mandate_amount(user, None)
                    output_file, error = exch_backend.generate_bank_mandate(user.id, mandate_amount)
                    if output_file is None:
                        return HttpResponse(error, status=404)
                    output_file = output_file.split('/')[-1]
                    prefix = 'webapp'
                    my_file_path = prefix + constants.STATIC + output_file
                    my_file = open(my_file_path, "rb")
                    content_type = 'application/pdf'
                    response = HttpResponse(my_file, content_type=content_type, status=200)
                    response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id) + '_mandate.pdf'
                    my_file.close()
                    return response  # contains the pdf of the pertinent user

            # file doesn't exist because investor vault is incomplete.
            return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)
