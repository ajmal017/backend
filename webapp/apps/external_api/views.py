from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.views.generic import View

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions

from . import investor_info_generation, bse_investor_info_generation, bulk_order_entry, kyc_pdf_generator, xsip_registration, bank_mandate
from core.models import OrderDetail, RedeemDetail
from . import models, constants, serializers, cvl
from api import utils as api_utils
from profiles.utils import is_investable
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
            return api_utils.response({"verifiable" : True, "message" : constants.YES_DOORSTEP_VERIFICATION})
        return api_utils.response({"verifiable" : False, "message" : constants.NO_DOORSTEP_VERIFICATION})


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
        if payment_constant.bank_product_id_map.get(bank_detail.name, ["",""]) == ["", ""]:
            return api_utils.response({constants.MESSAGE: constants.UNSUPPORTED_BANK}, status.HTTP_404_NOT_FOUND,
                                      constants.UNSUPPORTED_BANK)
        serializer = serializers.BankInfoGetSerializer(bank_detail)
        return api_utils.response(serializer.data)


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
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'application/pdf'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id) + "_" + time.strftime("%Y%m%d-%H%M%S") + "_investor.pdf"
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
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'application/pdf'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id)+'_kyc.pdf'
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
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id)+'_order.txt'
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
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id)+'_xip_order.txt'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateBankMandate(View):
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
            order_items = order_detail.fund_order_items.all()
            if is_investable(order_detail.user):
                output_file = bank_mandate.generate_bank_mandate_file(order_detail.user, order_items).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(order_detail.id)+'_order.txt'
                my_file.close()
                return response  # contains the pipe file of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)


class GenerateBseInfoTiff(View):
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
            user = pr_models.User.objects.get(email=request.GET.get('email'))
            if is_investable(user) and user.signature != "":
                output_file = bse_investor_info_generation.bse_investor_info_generator(user.id).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'image/tiff'
                download_name = user.id
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % download_name+".tiff"
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
            redeem_detail = RedeemDetail.objects.get(redeem_id=request.GET.get('redeem_id'))
            redeem_items = redeem_detail.fund_redeem_items.all()
            if is_investable(redeem_detail.user):
                output_file = bulk_order_entry.generate_redeem_pipe_file(redeem_detail.user, redeem_items).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'text/plain'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(redeem_detail.id)+'redeem.txt'
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
            user = pr_models.User.objects.get(email=request.GET.get('email'))
            if is_investable(user) and user.signature != "":
                output_file = bank_mandate.generate_bank_mandate_pdf(user.id).split('/')[-1]
                prefix = 'webapp'
                my_file_path = prefix+constants.STATIC + output_file
                my_file = open(my_file_path, "rb")
                content_type = 'application/pdf'
                response = HttpResponse(my_file, content_type=content_type, status=200)
                response['Content-Disposition'] = 'attachment;filename=%s' % str(user.id)+'_mandate.pdf'
                my_file.close()
                return response  # contains the pdf of the pertinent user
            else:
                # file doesn't exist because investor vault is incomplete.
                return HttpResponse(payment_constant.CANNOT_GENERATE_FILE, status=404)
        else:
            # non-admin is trying to access the file. Prevent access.
            return HttpResponse(constants.FORBIDDEN_ERROR, status=403)