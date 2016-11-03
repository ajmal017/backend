from django.shortcuts import render
from django.db import transaction
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions

from . import models, constants, serializers, utils, helpers
from api import utils as api_utils
from core import utils as core_utils
from core import models as core_models
from external_api import api
from external_api import models as external_models
from webapp.apps import generate_error_message, code_generator

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from copy import deepcopy
import functools
import logging
import warnings
import logging
import threading

from django.core.files.base import ContentFile
import urllib.request as urllib2


## Yeti Social Login
from rest_framework.response import Response
from social.apps.django_app.utils import load_strategy
from social.apps.django_app.utils import load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.exceptions import AuthAlreadyAssociated


def deprecate_current_app(func):
    """
    Handle deprecation of the current_app parameter of the views.
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            warnings.warn(
                "Passing `current_app` as a keyword argument is deprecated. "
                "Instead the caller of `{0}` should set "
                "`request.current_app`.".format(func.__name__),
                RemovedInDjango20Warning
            )
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)
    return inner


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
@deprecate_current_app
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    logger = logging.getLogger('django.debug')
    logger.debug("Profiles: views: password_reset_confirm")
    
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        logger.debug("Profiles: views: password_reset_confirm: Valid link")
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                request.session['email'] = user.email
                user.email_verified = True
                user.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        logger.debug("Profiles: views: password_reset_confirm: Invalid link")
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@deprecate_current_app
def password_reset_complete(request,
                            template_name='registration/password_reset_complete.html',
                            extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': _('Password reset complete'),
    }
    if extra_context is not None:
        context.update(extra_context)
    context.update({'email': request.session['email']})
    request.session['email'] = None
    return TemplateResponse(request, template_name, context)

#investor info check
def investor_info_check(user):
    applicant_name = None
    try:
        investor_info = models.InvestorInfo.objects.get(user=user)       
        if investor_info is not None:
            if investor_info.applicant_name is not None:
                applicant_name = investor_info.applicant_name       
    except models.InvestorInfo.DoesNotExist:
            applicant_name = None
    return applicant_name


        
class UserInfo(APIView):
    """
    Retrieve, update or delete a profile instance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        GET user data
        """
        serializer = serializers.UserSerializer(request.user)
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response(serializer.errors, status.HTTP_400_BAD_REQUEST, constants.PROFILE_GET_ERROR)

    def put(self, request, format=None):
        """
        :param request:
        Update user
        """
        name_array = request.data.get("name", "").split()
        serializer = serializers.UserSerializer(request.user, data=request.data)
        serializer.initial_data['first_name'] = name_array[0]  # First word is considered as first name
        serializer.initial_data['last_name'] = " ".join(name_array[1:])
        if serializer.is_valid():
            serializer.save(image=request.FILES.get('image'))
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class Register(APIView):
    """
    Register views
    """

    def post(self, request, format=None):
        """
        Api to register user
        We are setting the email given as username too.
        """
        # TODO: make things atomic
        flag = False
        user = None
        serializer = serializers.UserRegisterSerializer(data=request.data)
        email = serializer.initial_data.get("email")
        password = serializer.initial_data.get("password")
        phone = serializer.initial_data.get("phone_number")
        kwargs = {'email': email, 'phone_number': phone, 'password': password}
        utils.check_existing_user(**kwargs)
        result = utils.get_situation(**kwargs)
        kwargs.pop('password')
        if result in (0, 2):
            return api_utils.response({"message": constants.SIGNUP_ERROR, "signup_error": result},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.USER_ALREADY_EXISTS)
        elif result == 3:
            flag = True
        elif result in (1, 6):
            flag = False
            user = models.User.objects.get(**kwargs)
            user.set_password(password)
            user.save()
            serializer = serializers.UserRegisterSerializer(user, data=request.data)
        elif result == 4:
            return api_utils.response({"message": constants.SIGNUP_ERROR, "signup_error": result}, status.HTTP_404_NOT_FOUND,
                                      constants.EMAIL_EXISTS)
        elif result == 5:
            return api_utils.response({"message": constants.SIGNUP_ERROR, "signup_error": result}, status.HTTP_404_NOT_FOUND,
                                      constants.PHONE_EXISTS)
        if serializer.is_valid():
            if flag:
                username = serializer.validated_data.get("email")
                user = models.User.objects.create_user(email=email, username=username, password=password, phone_number=phone)
            user.image = request.FILES.get("image", None)
            user.identity_info_image = request.FILES.get("image", None)
            user.save()
            user_response = dict(serializer.data)
            user_response['risk_score'], user_response['name'] = None, ""
            sms_code = utils.get_sms_verification_code(user)
            # TODO : add provisions to add country code?
            send_sms_thread = threading.Thread(target=api.send_sms, args=(constants.OTP.format(sms_code), int(phone),))
            send_sms_thread.start()
            #sms_code_sent = api.send_sms(constants.OTP.format(sms_code), int(phone))
            code = code_generator(50)
            models.EmailCode.objects.update_or_create(
                user=user, defaults={'code': code, 'expires_at': datetime.now() + timedelta(hours=24)})
            
            # check the user has invester info 
            applicant_name = investor_info_check(request.user)
            
            helpers.send_verify_email(user, applicant_name, code, use_https=settings.USE_HTTPS)

            return api_utils.response({"user": user_response, "tokens": helpers.get_access_token(user, password),
                                       "assess": core_utils.get_assess_answer(user),
                                       "plan": core_utils.get_plan_answers(user),
                                       "retirement": core_utils.get_category_answers(user, "retirement"),
                                       "tax": core_utils.get_category_answers(user, "tax"),
                                       "invest": core_utils.get_invest_answers(user),
                                       "education": core_utils.get_category_answers(user, "education"),
                                       "wedding": core_utils.get_category_answers(user, "wedding"),
                                       "property": core_utils.get_category_answers(user, "property"),
                                       "event": core_utils.get_category_answers(user, "event"),
                                       })
        else:
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))


class Login(APIView):
    """
    Login user api
    """

    def post(self, request, *args, **kwargs):
        """
        The login_error cases:
        0 - user serializer errors
        1 - user with the given email or phone does not exist.
        2 - both email and phone not verified hence not able to login.
        3 - phone_number is not verified.
        4 - email is not verified.
        5 - incorrect password entered.
        6 - non-active user.

        :param request:
        An internal call to /o/token/ is sent to get access token which is then returned as response
        """
        login_error = constants.LOGIN_ERROR_0  # login_error holds the type of error generated.
        username = request.data.get('username')
        password = request.data.get('password')
        phone_number = None
        email_id = None
        try:
            if '@' in username:
                email_id = username
                user = models.User.objects.get(email__iexact=username)
            else:
                phone_number = username
                user = models.User.objects.get(phone_number=username)
        except models.User.DoesNotExist:
            login_error = constants.LOGIN_ERROR_1
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.NON_EXISTENT_USER_ERROR)
        if not user.phone_number_verified and not user.email_verified:
            login_error = constants.LOGIN_ERROR_2
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.PHONE_AND_EMAIL_NOT_VERIFIED)
        if phone_number and not user.phone_number_verified:
            login_error = constants.LOGIN_ERROR_3
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.PHONE_NOT_VERIFIED)
        if email_id and not user.email_verified:
            login_error = constants.LOGIN_ERROR_4
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.EMAIL_NOT_VERIFIED)

        serializer = serializers.UserRegisterSerializer(user)
        if serializer.is_valid:
            if user.is_active:
                if user.check_password(password):
                    return api_utils.response({"user": serializer.data,
                                               "tokens": helpers.get_access_token(user, password),
                                               "assess": core_utils.get_assess_answer(user),
                                               "plan": core_utils.get_plan_answers(user),
                                               "retirement": core_utils.get_category_answers(user, "retirement"),
                                               "tax": core_utils.get_category_answers(user, "tax"),
                                               "invest": core_utils.get_category_answers(user, "invest"),
                                               "education": core_utils.get_category_answers(user, "education"),
                                               "wedding": core_utils.get_category_answers(user, "wedding"),
                                               "property": core_utils.get_category_answers(user, "property"),
                                               "event": core_utils.get_category_answers(user, "event")})
                else:
                    login_error = constants.LOGIN_ERROR_5
                    return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                              status.HTTP_404_NOT_FOUND,
                                              constants.LOGIN_ERROR)
            else:
                login_error = constants.LOGIN_ERROR_6
                return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                          status.HTTP_404_NOT_FOUND,
                                          constants.NON_ACTIVE_USER_ERROR)
        else:
            login_error = constants.LOGIN_ERROR_0
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))


class ProfileCompleteness(APIView):
    """
    ProfileCompleteness user api
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        :param request:
        An internal call to /o/token/ is sent to get access token which is then returned as response
        """
        user = request.user
        if user:
            data = {"assess": core_utils.get_assess_answer(user), "plan": core_utils.get_plan_answers(user),
                    "retirement": core_utils.get_category_answers(user, "retirement"),
                    "tax": core_utils.get_category_answers(user, "tax"),
                    "invest": core_utils.get_category_answers(user, "invest"),
                    "education": core_utils.get_category_answers(user, "education"),
                    "wedding": core_utils.get_category_answers(user, "wedding"),
                    "property": core_utils.get_category_answers(user, "property"),
                    "event": core_utils.get_category_answers(user, "event")}

            flag_data = {}
            for k, v in data.items():
                flag_data[k] = False if v == {} else True

            flag_data['track'] = False
            flag_data['vault_locked'] = user.vault_locked
            flag_data['bse_registered'] = user.bse_registered
            flag_data['vault'] = False if request.user.signature == "" else True
            flag_data['process_choice'] = None if request.user.process_choice == "" else request.user.process_choice
            flag_data['is_virtual_seen'] = user.is_virtual_seen
            flag_data['is_real_seen'] = user.is_real_seen

            try:
                investor_info = models.InvestorInfo.objects.get(user=request.user)
                flag_data['kra_verified'] = investor_info.kra_verified
            except models.InvestorInfo.DoesNotExist:
                flag_data['kra_verified'] = False

            try:
                investor_bank_details = models.InvestorBankDetails.objects.get(user=request.user)
                if investor_bank_details.ifsc_code:
                    flag_data['is_bank_supported'] = investor_bank_details.ifsc_code.is_supported
                else:
                    flag_data['is_bank_supported'] = False
            except models.InvestorBankDetails.DoesNotExist:
                flag_data['is_bank_supported'] = False

            flag_data['is_virtual'] = False
            if request.user.orderdetail_set.all().count() == 0:
                flag_data['is_virtual'] = True

            try:
                portfolio = core_models.Portfolio.objects.get(user=request.user, has_invested=False)
                flag_data['portfolio'] = True
                portfolio_last_modified = portfolio.modified_at
                try:
                    answer_last_modified = core_models.Answer.objects.filter(
                        user=request.user, portfolio=None).latest("modified_at").modified_at
                    if answer_last_modified > portfolio_last_modified:
                        flag_data['rebuild_portfolio'] = True
                    elif request.user.rebuild_portfolio:
                        flag_data['rebuild_portfolio'] = True
                    else:
                        flag_data['rebuild_portfolio'] = False
                except core_models.Answer.DoesNotExist as e:
                    flag_data['rebuild_portfolio'] = True


            except core_models.Portfolio.DoesNotExist:
                flag_data['portfolio'] = False
                flag_data['invest_redeem'] = False
                flag_data['rebuild_portfolio'] = True


            if core_models.OrderDetail.objects.filter(user=request.user):
                flag_data['invest_redeem'] = True
            else:
                flag_data['invest_redeem'] = False

            flag_data['email_verified'] = user.email_verified
            flag_data['phone_number_verified'] = user.phone_number_verified
            flag_data['show_redeem'] = core_utils.has_redeemable_funds(user)

            return api_utils.response({"user_answers": data, "user_flags": flag_data})


class ResetPassword(APIView):
    """
    Reset password api which essentally just check if its a email of a valid user who is active and sends a resset
    passsword link to them
    """

    def post(self, request, *args, **kwargs):
        """
        :param request:
        Changes password to newer password set
        """
        email = request.data.get('email')
        # TODO: Check if this is valid email using soe tech
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return api_utils.response({"message": constants.INCORRECT_EMAIL}, status.HTTP_404_NOT_FOUND,
                                      constants.INCORRECT_EMAIL)
        if user.is_active:
            if user.email_verified:
                applicant_name = investor_info_check(user)
                helpers.send_reset_email(user=user,applicant_name=applicant_name,use_https=settings.USE_HTTPS)
                return api_utils.response({"message": constants.RESET_EMAIL_SENT, "case": 1})
            else:
                sms_code = utils.get_sms_verification_code(user)
                # TODO : add provisions to add country code?
                sms_code_sent = api.send_sms(constants.FORGOT_PASSWORD_OTP.format(sms_code), int(user.phone_number))
                return api_utils.response({"message": constants.VERIFY_SMS_SENT, "case": 2},
                                          status.HTTP_200_OK)
        else:
            return api_utils.response({"message": constants.UNABLE_TO_RESET}, status.HTTP_404_NOT_FOUND,
                                      constants.NON_ACTIVE_USER_ERROR)


class ChangePassword(APIView):
    """
    Change password api which essentailly just check if its a email of a valid user who is active and change password
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        :param request:
        Changes password to newer password set
        """
        user = request.user
        if request.data.get("old_password") and request.data.get("new_password"):
            if user.is_active:
                if user.check_password(request.data.get("old_password")):
                    user.set_password(request.data.get("new_password"))
                    user.save()
                    return api_utils.response({"message": constants.PASSWORD_CHANGED})
                else:
                    return api_utils.response({"message": constants.INCORRECT_OLD_PASSWORD}, status.HTTP_404_NOT_FOUND,
                                              constants.INCORRECT_OLD_PASSWORD)
            else:
                return api_utils.response({"message": constants.NON_ACTIVE_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                          constants.NON_ACTIVE_USER_ERROR)
        else:
            return api_utils.response({"message": constants.MALFORMED_REQUEST}, status.HTTP_404_NOT_FOUND,
                                      constants.MALFORMED_REQUEST)


class VerifyPhone(APIView):
    """
    Verifies the users phone
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        :param request:
        Verifies the users phone
        """
        if not request.user.phone_number_verified:
            verification_object = models.VerificationSMSCode.objects.get(user=request.user)
            if verification_object:
                if verification_object.sms_code == request.data.get('sms_code', 00000):
                    request.user.phone_number_verified = True
                    request.user.save()
                    verification_object.delete()
                    return api_utils.response({"message": constants.PHONE_VERIFIED})
                else:
                    return api_utils.response({"message": constants.INCORRECT_SMS_CODE}, status.HTTP_404_NOT_FOUND,
                                              constants.INCORRECT_SMS_CODE)
            else:
                return api_utils.response({"message": constants.NON_EXISTENT_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                          constants.NON_EXISTENT_USER_ERROR)
        return api_utils.response({"message": constants.PHONE_ALREADY_VERIFIED})


class ResendVerifyEmail(APIView):
    """
    Send a verification email to user given email address
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        flag_data = {}
        
        user = request.user
        if user.is_active:
            code = code_generator(50)
            models.EmailCode.objects.update_or_create(
                user=user, defaults={'code': code, 'expires_at': datetime.now() + timedelta(hours=24)})
            
            applicant_name = investor_info_check(request.user)
            
            helpers.send_verify_email(user=user,applicant_name=applicant_name,code=code, use_https=settings.USE_HTTPS)
            return api_utils.response({"message": constants.VERIFY_EMAIL_SENT})
        else:
            return api_utils.response({"message": constants.NON_ACTIVE_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                      constants.NON_ACTIVE_USER_ERROR)


class ResendVerifyPhone(APIView):
    """
    Send a verification sms to user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        user = request.user
        if user.is_active:
            sms_code = utils.get_sms_verification_code(user)
            # TODO : add provisions to add country code?
            sms_code_sent = api.send_sms(constants.OTP.format(sms_code), int(user.phone_number))
            if sms_code_sent == 1:  # This is 1 because send_sms gives the number of successfully sms sent
                return api_utils.response({"message": constants.VERIFY_SMS_SENT, "sms_code_sent": sms_code_sent})
            return api_utils.response({"message": constants.VERIFY_SMS_NOT_SENT, "sms_code_sent": sms_code_sent})
        else:
            return api_utils.response({"message": constants.NON_ACTIVE_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                      constants.NON_ACTIVE_USER_ERROR)

class ResendForgotPassword(APIView):
    """
    Send a verification sms to user
    """

    def post(self, request):
        """
        :param request:
        :return:
        """
        email = request.data.get('email')
        # TODO: Check if this is valid email using soe tech
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return api_utils.response({"message": constants.INCORRECT_EMAIL}, status.HTTP_404_NOT_FOUND,
                                      constants.INCORRECT_EMAIL)
        if user.is_active:
            sms_code = utils.get_sms_verification_code(user)
            # TODO : add provisions to add country code?
            sms_code_sent = api.send_sms(constants.FORGOT_PASSWORD_OTP.format(sms_code), int(user.phone_number))
            return api_utils.response({"message": constants.VERIFY_SMS_SENT, "sms_code_sent": sms_code_sent})
        else:
            return api_utils.response({"message": constants.NON_ACTIVE_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                      constants.NON_ACTIVE_USER_ERROR)


class ResendVerifyEmailAdmin(APIView):
    """
    Send a verification sms to user
    """

    def post(self, request):
        """
        :param request:
        :return:
        """
        flag_data = {}
        
        user = models.User.objects.get(email=request.data.get('email'))
        if user.is_active:
            code = code_generator(50)
            models.EmailCode.objects.update_or_create(
                user=user, defaults={'code': code, 'expires_at': datetime.now() + timedelta(hours=24)})
            
            # Check user info in Invest info table
            applicant_name = investor_info_check(request.user)
            
            helpers.send_verify_email(user=user,applicant_name=applicant_name, code=code, use_https=settings.USE_HTTPS)
            return api_utils.response({"message": constants.RESEND_MAIL_SUCCESS})
        else:
            return api_utils.response({"message": constants.RESEND_MAIL_FAILURE}, status.HTTP_404_NOT_FOUND,
                                      constants.RESEND_MAIL_FAILURE)


class CheckEmailCode(APIView):
    """
    Checks if the code sent by user is same as one stored
    """

    def get(self, request, token):
        """
        :param request:
        :param token:an alphanumeric token of length 50.
        :return:
        """
        try:
            code_entry = models.EmailCode.objects.select_related("user").get(code=token)
        except models.EmailCode.DoesNotExist:
            return render(request, 'verify_email/email_verified.html', {'user': None, 'verification_allowed': 0})

        user = code_entry.user
        if code_entry.expires_at >= datetime.now():
            user.email_verified = True
            user.save()
            code_entry.delete()
            return render(request, 'verify_email/email_verified.html', {'user': user, 'verification_allowed': 1})
        else:
            return render(request, 'verify_email/email_verified.html', {'user': user, 'verification_allowed': 0})


class SaveImage(APIView):
    """
    To save images of the user based on the type of the image as mentioned in the request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request: http request with the user and the image type to be updated.
        :return: message on successful image store.
        """
        if request.data.get('identity_info_image', None):
            """
            This method accepts a image file and updates the identity image.

            :return:  'Identity Image saved' with the url of saved image on successful image store.
            """
            serializer = serializers.SaveIdentityImageSerializer(data=request.data)
            if serializer.is_valid():
                user = models.User.objects.get(id=request.user.id)
                user.identity_info_image = request.FILES.get("identity_info_image", None)
                if user.image == "":
                    user.image = request.FILES.get("identity_info_image", None)
                user.save()
                return api_utils.response({"message": constants.IDENTITY_IMAGE_SAVED,
                                           "identity_info_image": user.identity_info_image.url,"identity_info_image_thumbnail": user.identity_info_image_thumbnail.url},
                                           status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))

        elif request.data.get('pan_image', None):
            """
            This method accepts a image file and updates the investors pan card image.

            :return: 'Image saved' response on successful image store.
            """
            investor, created = models.InvestorInfo.objects.get_or_create(user=request.user)
            serializer = serializers.SavePanImageSerializer(investor, data=request.data)
            if serializer.is_valid():
                investor.pan_image = request.FILES.get('pan_image', None)
                investor.save()
                return api_utils.response({"message": constants.PAN_IMAGE_SAVED, "pan_image": investor.pan_image.url,
                                           "pan_image_thumbnail": investor.pan_image_thumbnail.url},
                                          status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))

        elif request.data.get('front_image', None):
            """
            This method accepts a image file and updates the contact info front_image
            It also accepts an address proof type and saves the image only if address proof type is given.
            It also sets the boolean flag is_contact_info to True if and only if the front image is saved.

            :return: success response on successful image store.
            """
            contact, created = models.ContactInfo.objects.get_or_create(user=request.user)
            if not request.data.get('address_proof_type', None):
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.MALFORMED)
            serializer = serializers.ContactInfoContinueSerializer(contact, data=request.data)
            if serializer.is_valid():
                addr_proof = serializer.initial_data.get('address_proof_type', 1)
                serializer.save(front_image=request.FILES.get('front_image', None), address_proof_type=addr_proof)
                return api_utils.response({"message": constants.SUCCESS, "front_image": contact.front_image.url,"front_image_thumbnail": contact.front_image_thumbnail.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

        elif request.data.get('back_image', None):
            """
            This method accepts a image file and updates the contact info back_image

            :param request: will contain the back_image.
            :return: success response on successful image store.
            """
            contact, created = models.ContactInfo.objects.get_or_create(user=request.user)
            if request.data.get('address_proof_type', None):
                request.data.pop('address_proof_type')
            serializer = serializers.ContactInfoContinueSerializer(contact, data=request.data)
            if serializer.is_valid():
                serializer.save(back_image=request.FILES.get('back_image', None))
                return api_utils.response({"message": constants.SUCCESS, "back_image": contact.back_image.url,"back_image_thumbnail": contact.back_image_thumbnail.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

        elif request.data.get('permanent_front_image', None):
            """
            This method accepts a image file and updates the contact info permanent_front_image
            It also accepts an permanent_address_proof_type and saves the image only if address proof type is given.

            :return: success response on successful image store.
            """
            contact, created = models.ContactInfo.objects.get_or_create(user=request.user)
            if not request.data.get('permanent_address_proof_type', None):
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.MALFORMED)
            serializer = serializers.ContactInfoContinueSerializer(contact, data=request.data)
            if serializer.is_valid():
                addr_proof = serializer.initial_data.get('permanent_address_proof_type', 1)
                serializer.save(permanent_front_image=request.FILES.get('permanent_front_image', None),
                                permanent_address_proof_type=addr_proof)
                return api_utils.response({"message": constants.SUCCESS, "permanent_front_image": contact.permanent_front_image.url,"permanent_front_image_thumbnail": contact.permanent_front_image_thumbnail.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

        elif request.data.get('permanent_back_image', None):
            """
            This method accepts a image file and updates the contact info permanent_back_image

            :param request: will contain the permanent_back_image.
            :return: success response on successful image store.
            """
            contact, created = models.ContactInfo.objects.get_or_create(user=request.user)
            if request.data.get('permanent_address_proof_type', None):
                request.data.pop('permanent_address_proof_type')
            serializer = serializers.ContactInfoContinueSerializer(contact, data=request.data)
            if serializer.is_valid():
                serializer.save(permanent_back_image=request.FILES.get('permanent_back_image', None))
                return api_utils.response({"message": constants.SUCCESS, "permanent_back_image": contact.permanent_back_image.url,"permanent_back_image_thumbnail": contact.permanent_back_image_thumbnail.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

        elif request.data.get('signature', None):
            """
            This method accepts a image file and updates the signature image.

            :return: 'Signature saved' response on successful image store.
            """

            serializer = serializers.SaveSignatureSerializer(request.user, data=request.data)
            if serializer.is_valid():
                request.user.signature = request.FILES.get('signature', None)
                request.user.finaskus_id = core_utils.get_finaskus_id(request.user)
                request.user.save()
                helpers.send_vault_completion_email(request.user, request.user.email, use_https=settings.USE_HTTPS)
                return api_utils.response({"message": constants.SIGNATURE_SAVED,
                                           "signature": request.user.signature.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))

        elif request.data.get('nominee_signature', None):
            """
            This method accepts a image file and updates the nominee_signature image.

            :return: 'Signature saved' response on successful image store.
            """
            nominee, created = models.NomineeInfo.objects.get_or_create(user=request.user)
            serializer = serializers.SaveNomineeSignatureSerializer(nominee, data=request.data)
            if serializer.is_valid():
                serializer.save(nominee_signature=request.FILES.get('nominee_signature', None))
                return api_utils.response({"message": constants.SIGNATURE_SAVED,
                                           "signature": nominee.nominee_signature.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))

        elif request.data.get('bank_cheque_image', None):
            """
            This method accepts a image file and updates the bank_cheque_image image.
            :return:
            """

            bank_info, created = models.InvestorBankDetails.objects.get_or_create(user=request.user)
            serializer = serializers.BankChequeSerializer(bank_info, data=request.data)
            if serializer.is_valid():
                serializer.save(bank_cheque_image=request.FILES.get('bank_cheque_image', None))
                return api_utils.response({"message": constants.BANK_CHEQUE_SAVED,
                                           "bank_cheque_image": bank_info.bank_cheque_image.url,"bank_cheque_image_thumbnail": bank_info.bank_cheque_image_thumbnail.url}, status.HTTP_200_OK)
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))
        else:
            return api_utils.response({"message": constants.MALFORMED}, status.HTTP_400_BAD_REQUEST)


class EmailStatus(APIView):
    """
    Sends the current email verification status of a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:  Sends the current email verification status of a user
        """
        serializer = serializers.EmailStatusSerializer(request.user)
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class ChangeEmail(APIView):
    """
    Sends the current email verification status of a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:  Sends the current email verification status of a user
        """
        flag_data={}
        serializer = serializers.EmailStatusSerializer(request.user, data=request.data)
        if serializer.is_valid():
            old_email = request.user.email
            # check user information in investor information 
            applicant_name = investor_info_check(request.user)
            helpers.send_email_change_notify_to_old_email(old_email,applicant_name, serializer.validated_data.get('email'),
                                                          use_https=settings.USE_HTTPS)
            user = serializer.save(email_verified=False, username=serializer.validated_data.get('email'))
            code = code_generator(50)

            models.EmailCode.objects.update_or_create(
                user=user, defaults={'code': code, 'expires_at': datetime.now() + timedelta(hours=24)})
            
            helpers.send_verify_email(user=user,applicant_name=applicant_name, code=code, use_https=settings.USE_HTTPS)
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class InvestorInfo(APIView):
    """
    Contains method to add, update and get investor info
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Displays data of the pertinent investor.
        
        :param request: the http request which contains the user.
        :return: returns the investor_info for the pertinent investor.
        """
        try:
            investor = models.InvestorInfo.objects.get(user=request.user)
        except models.InvestorInfo.DoesNotExist:
            response = {
                "id": None,
                "dob": None,
                "investor_status": "Resident Individual",
                "pan_number": None,
                "applicant_name": None,
                "father_name": None,
                "income": None,
                "political_exposure": None,
                "occupation_type": None,
                "occupation_specific": "",
                "other_tax_payer": False,
                "pan_image": None,
                "pan_image_thumbnail":None
            }
            return api_utils.response(response)
        serializer = serializers.InvestorInfoDateSerializer(investor)
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

    def post(self, request):
        """
        This allows us to create/update new Investor info records
        
        :param request: the http request which contains the user
        :return:  Sends the status of new investor creation
        """
        payload_data = None
        try:
            investor = models.InvestorInfo.objects.get(user=request.user)
        except models.InvestorInfo.DoesNotExist:
            investor = None
        request_data_copy = deepcopy(request.data)
        request_data_copy.pop("pan_number")
        if investor and investor.kra_verified:
            request_data_copy.pop("applicant_name")
        serializer = serializers.InvestorInfoSerializer(data=request_data_copy)
        if serializer.is_valid():
            models.InvestorInfo.objects.update_or_create(user=request.user, defaults=serializer.data)
            utils.set_user_check_attributes(request.user, 'is_investor_info')
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class PincodeInfo(APIView):
    """
    This view retrieves the details of a Pincode.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """This allows us to view details of the pertinent pincode

        :param request: the http request which contains the pincode as part of post data.
        :return:  Sends the details ( pincode, office ) of the pertinent pincode
        """
        target_pincode = request.data.get('pincode', None)
        result = models.Pincode.objects.filter(pincode=target_pincode)
        if len(result) == 0:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.PINCODE_DOES_NOT_EXIST)
        serializer = serializers.PincodeSerializer(result[0])
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class ContactInfo(APIView):
    """
    displays Contact Information of the pertinent investor
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Displays CONTACT INFO of the pertinent investor

        :param request: the http request which contains the user.
        :return: returns the contact_info for the pertinent investor.
        """
        try:
            contact = models.ContactInfo.objects.get(user=request.user)
        except models.ContactInfo.DoesNotExist:
            return_data = constants.DEFAULT_CONTACT_INFO
            return_data["email"] = request.user.email
            return_data["phone_number"] = request.user.phone_number
            return api_utils.response(return_data)
        serializer = serializers.ContactInfoSerializer(contact)
        if serializer.is_valid:
            if contact.communication_address:
                comm_address_pincode_serializer = serializers.PincodeSerializer(contact.communication_address.pincode)
                serializer.data['communication_address'].update(comm_address_pincode_serializer.data)
            if contact.permanent_address:
                permanent_address_pincode_serializer = serializers.PincodeSerializer(contact.permanent_address.pincode)
                serializer.data['permanent_address'].update(permanent_address_pincode_serializer.data)
            response = serializer.data
            if not serializer.data["phone_number"]:
                response.update({"phone_number": request.user.phone_number})
            if not serializer.data["email"]:
                response.update({"email": request.user.email})
            return api_utils.response(response)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

    def post(self, request):
        """
        creates CONTACT INFO of the pertinent investor

        :param request: the http request which contains the user, contact info details in the post data
        :return: returns a success message on successful completion.
        """
        flag = False
        contact = None
        # with transaction.atomic():
        try:
            contact = models.ContactInfo.objects.get(user=request.user)
            flag = True
        except models.ContactInfo.DoesNotExist:
            pass
        is_succesful, data = utils.generate_address(request.data.get('communication_address'))
        if not is_succesful:
            return api_utils.response({"field": "communication_address"}, status.HTTP_400_BAD_REQUEST,
                                      constants.INCORRECT_PINCODE_SET)
        if flag:
            comm_addr = serializers.AddressSerializer(contact.communication_address, data=data)
        else:
            comm_addr = serializers.AddressSerializer(data=data)
        if comm_addr.is_valid():
            comm_obj = comm_addr.save()
        else:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(comm_addr.errors))
        if not request.data.get('address_are_equal'):
            is_succesful, data = utils.generate_address(request.data.get('permanent_address'))
            if not is_succesful:
                return api_utils.response({"field": "permanent_address"},
                               status.HTTP_400_BAD_REQUEST, constants.INCORRECT_PINCODE_SET)
            if flag:
                perm_addr = serializers.AddressSerializer(contact.permanent_address, data=data)
            else:
                perm_addr = serializers.AddressSerializer(data=data)
            if perm_addr.is_valid():
                perm_obj = perm_addr.save()
            else:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(perm_addr.errors))
            models.ContactInfo.objects.update_or_create(
                user=request.user, defaults={"communication_address_id": comm_obj.id,
                                             "permanent_address_id": perm_obj.id,
                                             "address_are_equal": False,
                                             "email": request.data.get('email', None),
                                             "phone_number":  request.data.get('phone_number', None),
                                             "communication_address_type": request.data.get('communication_address_type', None)})
            utils.set_user_check_attributes(request.user, 'is_contact_info')
        else:
            perm_obj = comm_obj
            perm_obj.id = None
            perm_obj.save()
            models.ContactInfo.objects.update_or_create(
                user=request.user, defaults={"communication_address_id": comm_obj.id,
                                             "permanent_address_id": perm_obj.id,
                                             "address_are_equal": True,
                                             "email": request.data.get('email', None),
                                             "phone_number":  request.data.get('phone_number', None),
                                             "communication_address_type": request.data.get('communication_address_type', None)})
            utils.set_user_check_attributes(request.user, 'is_contact_info')
        return api_utils.response({"message": constants.SUCCESS})


class ContactInfoSkip(APIView):
    """
    has method to create or update contact info.
    this is for the skip button
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        creates CONTACT INFO of the pertinent investor

        :param request: the http request which contains the user, contact info details in the post data
        :return: returns a success message on successful completion.
        """
        flag = False
        contact = None
        with transaction.atomic():
            try:
                contact = models.ContactInfo.objects.get(user=request.user)
                flag = True
            except models.ContactInfo.DoesNotExist:
                pass
            is_succesful, data = utils.generate_address(request.data.get('communication_address'))
            if not is_succesful:
                return api_utils.response({"field": "communication_address"}, status.HTTP_400_BAD_REQUEST,
                                          constants.INCORRECT_PINCODE_SET)
            if flag:
                comm_addr = serializers.AddressSkipSerializer(contact.communication_address, data=data)
            else:
                comm_addr = serializers.AddressSkipSerializer(data=data)
            if comm_addr.is_valid():
                comm_obj = comm_addr.save()
            else:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(comm_addr.errors))
            if not request.data.get('address_are_equal'):
                is_succesful, data = utils.generate_address(request.data.get('permanent_address'))
                if not is_succesful:
                    return api_utils.response({"field": "permanent_address"},
                                   status.HTTP_400_BAD_REQUEST, constants.INCORRECT_PINCODE_SET)
                if flag:
                    perm_addr = serializers.AddressSkipSerializer(contact.permanent_address, data=data)
                else:
                    perm_addr = serializers.AddressSkipSerializer(data=data)
                if perm_addr.is_valid():
                    perm_obj = perm_addr.save()
                else:
                    return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(perm_addr.errors))
                models.ContactInfo.objects.update_or_create(
                    user=request.user, defaults={"communication_address_id": comm_obj.id,
                                                 "permanent_address_id": perm_obj.id,
                                                 "address_are_equal": False,
                                                 "email": request.data.get('email', None),
                                                 "phone_number":  request.data.get('phone_number', None)})
            else:
                models.ContactInfo.objects.update_or_create(
                    user=request.user, defaults={"communication_address_id": comm_obj.id,
                                                 "permanent_address_id": comm_obj.id,
                                                 "address_are_equal": True,
                                                 "email": request.data.get('email', None),
                                                 "phone_number":  request.data.get('phone_number', None)})
            return api_utils.response({"message": constants.SUCCESS})


class IdentityInfo(APIView):
    """
    Contains method to update and get user marital_status, gender, nationality.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Displays marital_status, gender, nationality  of the pertinent user.

        :param request: the http request which contains the user.
        :return: returns the (marital_status, gender and nationality) for the pertinent user.
        """
        try:
            target_user = models.User.objects.get(id=request.user.id)
        except models.User.DoesNotExist:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_USER_ERROR)
        serializer = serializers.IdentityInfoGetSerializer(target_user)
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

    def post(self, request):
        """
        This allows us to update user marital_status, gender, nationality.

        :param request: the http request which contains the user
        :return:  Sends the newly updated marital_status, gender and nationality of the user
        """
        serializer = serializers.IdentityInfoSerializer(request.user, data=request.data)
        if request.user.get_kra_verified():
            serializer = serializers.IdentityInfoOptionalSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            utils.set_user_check_attributes(request.user, 'is_identity_info')
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class IdentityInfoSkip(APIView):
    """
    Contains method to update user marital_status, gender, nationality.
    This is for the skip button
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        This allows us to update user marital_status, gender, nationality.

        :param request: the http request which contains the user
        :return:  Sends the newly updated marital_status, gender and nationality of the user
        """
        try:
            target_user = models.User.objects.get(id=request.user.id)
        except models.User.DoesNotExist:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_USER_ERROR)
        serializer = serializers.IdentityInfoSkipSerializer(target_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class IsCompleteView(APIView):
    """
    Contains method to get and display if user has completed details of investor_info, identity_info,
    contact_info, bank_info, nominee_info, terms and conditions and also declarations.

    It contains post methods to update declarations and terms booleans.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Displays details completed by the pertinent user.

        :param request: the http request which contains the user.
        :return: returns the status of the 7 booleans as mentioned above for the pertinent user.
        """
        return api_utils.response(utils.current_vault_status(request.user))

    def post(self, request):
        """
        This allows us to update the terms and conditions boolean as well as the declarations boolean if and only if
        all the other booleans are set.

        :param request: the http request which contains the user
        :return:  Sends the pan_number and the process_choice of the pertinent user.
        """

        if utils.is_investable(request.user):
            serializer = serializers.IsCompletePostSerializer(request.user, data=request.data)
            if serializer.is_valid():
                vaultLocked = request.user.vault_locked 
                serializer.save()
                request.user.vault_locked = True
                request.user.save()
                
                applicant_name = investor_info_check(request.user)
                    
                if vaultLocked == False:
                    helpers.send_vault_completion_email_user(request.user, applicant_name,request.user.email, use_https=settings.USE_HTTPS)
                return api_utils.response({'finaskus_id': request.user.finaskus_id,
                                           'process_choice': request.user.process_choice})
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))
        else:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.INVESTOR_INFO_INCOMPLETE)


class DeletePhonenumber(APIView):
    """
    Api to delete user by phone number

    """
    # TODO : Remove this after testing period ends

    def get(self, request):
        """
        Displays details completed by the pertinent user.

        :param request: the http request which contains the user.
        :return: returns the status of the 7 booleans as mentioned above for the pertinent user.
        """
        if request.query_params.get("phone"):
            try:
                target_user = models.User.objects.get(phone_number=request.query_params.get("phone"))
            except models.User.DoesNotExist:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_USER_ERROR)
        if request.query_params.get("email"):
            try:
                target_user = models.User.objects.get(email=request.query_params.get("email"))
            except models.User.DoesNotExist:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_USER_ERROR)
        target_user.delete()
        return api_utils.response({"message": "the user has been deleted."})


class NomineeInfo(APIView):
    """
    has methods to create or update and get Nominee Information of the pertinent nominee
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        displays the nominee information.
        :param request: http request which contains the user
        :return the nominee details.
        """
        try:
            target_nominee = models.NomineeInfo.objects.get(user=request.user)
        except models.NomineeInfo.DoesNotExist:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_CONTACT_NOMINEE_ERROR)
        serializer = serializers.NomineeInfoSerializer(target_nominee)
        if serializer.is_valid:
            if target_nominee.nominee_address:
                pincode_serializer = serializers.PincodeSerializer(target_nominee.nominee_address.pincode)
                serializer.data['nominee_address'].update(pincode_serializer.data)
            else:
                serializer.data['nominee_address'] = {}
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

    def post(self, request):
        """
        creates Nominee of the pertinent user.

        :param request: the http request which contains the user.
        :return: returns a success message on successful creation of the nominee.
        """
        flag = False
        nominee_addr = None
        nominee_info = None
        with transaction.atomic():
            if not request.data.get('nominee_absent'):
                if request.data.get('address_are_equal'):
                    models.NomineeInfo.objects.update_or_create(
                        user=request.user, defaults={"nominee_address_id": None,
                                                     "nominee_name": request.data.get('nominee_name'),
                                                     "nominee_dob": request.data.get('nominee_dob'),
                                                     "guardian_name": request.data.get('guardian_name'),
                                                     "relationship_with_investor":
                                                         request.data.get('relationship_with_investor'),
                                                     "nominee_absent": False,
                                                     "address_are_equal": True})
                else:
                    try:
                        nominee_info = models.NomineeInfo.objects.get(user=request.user)
                        flag = True
                    except models.NomineeInfo.DoesNotExist:
                        pass
                    is_succesful, data = utils.generate_address(request.data.get('nominee_address'))
                    if not is_succesful:
                        return api_utils.response({"field": "nominee_address"},
                                   status.HTTP_400_BAD_REQUEST, constants.INCORRECT_PINCODE_SET)
                    if flag:
                        nominee_addr = serializers.AddressSerializer(nominee_info.nominee_address, data=data)
                    nominee_addr = serializers.AddressSerializer(data=data)
                    if nominee_addr.is_valid():
                        nominee_addr_obj = nominee_addr.save()
                    else:
                        return api_utils.response({}, status.HTTP_400_BAD_REQUEST,
                                                  generate_error_message(nominee_addr.errors))
                    models.NomineeInfo.objects.update_or_create(
                        user=request.user, defaults={"nominee_address_id": nominee_addr_obj.id,
                                                     "nominee_name": request.data.get('nominee_name'),
                                                     "nominee_dob": request.data.get('nominee_dob'),
                                                     "guardian_name": request.data.get('guardian_name'),
                                                     "relationship_with_investor":
                                                         request.data.get('relationship_with_investor'),
                                                     "nominee_absent": False,
                                                     "address_are_equal": False})
            else:
                models.NomineeInfo.objects.update_or_create(user=request.user, defaults={"nominee_absent": True, })
            utils.set_user_check_attributes(request.user, 'is_nominee_info')
            return api_utils.response({"message": constants.SUCCESS}, status.HTTP_200_OK)


class NomineeInfoSkip(APIView):
    """
    has methods to create or update Nominee Information of the pertinent nominee
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        creates Nominee of the pertinent user.

        :param request: the http request which contains the user.
        :return: returns a success message on successful creation of the nominee.
        """
        with transaction.atomic():
            if not request.data.get('nominee_absent'):
                if request.data.get('address_are_equal'):
                    try:
                        contact_info = models.ContactInfo.objects.get(user=request.user)
                        nominee_addr_obj = contact_info.communication_address
                    except models.ContactInfo.DoesNotExist:
                        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.CONTACT_INFO_DOES_NOT_EXIST)

                    models.NomineeInfo.objects.update_or_create(
                        user=request.user, defaults={"nominee_address_id": nominee_addr_obj.id,
                                                     "nominee_name": request.data.get('nominee_name'),
                                                     "nominee_dob": request.data.get('nominee_dob'),
                                                     "guardian_name": request.data.get('guardian_name'),
                                                     "relationship_with_investor":
                                                         request.data.get('relationship_with_investor'),
                                                     "nominee_absent": False,
                                                     "address_are_equal": True})
                else:
                    is_succesful, data = utils.generate_address(request.data.get('nominee_address'))
                    if not is_succesful:
                        return api_utils.response({"field": "nominee_address"},
                                   status.HTTP_400_BAD_REQUEST, constants.INCORRECT_PINCODE_SET)
                    nominee_addr = serializers.AddressSerializer(data=data)
                    if nominee_addr.is_valid():
                        nominee_addr_obj = nominee_addr.save()
                    else:
                        return api_utils.response({}, status.HTTP_400_BAD_REQUEST,
                                                  generate_error_message(nominee_addr.errors))
                    models.NomineeInfo.objects.update_or_create(
                        user=request.user, defaults={"nominee_address_id": nominee_addr_obj.id,
                                                     "nominee_name": request.data.get('nominee_name'),
                                                     "nominee_dob": request.data.get('nominee_dob'),
                                                     "guardian_name": request.data.get('guardian_name'),
                                                     "relationship_with_investor":
                                                         request.data.get('relationship_with_investor'),
                                                     "nominee_absent": False,
                                                     "address_are_equal": False})
            else:
                models.NomineeInfo.objects.update_or_create(user=request.user, defaults={"nominee_absent": True, })
            return api_utils.response({"message": constants.SUCCESS}, status.HTTP_200_OK)


class AppointmentSchedule(APIView):
    """
    has methods to create or get appointment details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        This displays appointment schedule details.

        :param request: http request method that contains the user.
        :return: appointment schedule details.
        """
        try:
            target_appointment = models.AppointmentDetails.objects.get(user=request.user)
        except models.AppointmentDetails.DoesNotExist:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.NON_EXISTENT_APPOINTMENT_ERROR)
        serializer = serializers.AppointmentDetailsGetSerializer(target_appointment)
        if serializer.is_valid:
            if target_appointment.address:
                pincode_serializer = serializers.PincodeSerializer(target_appointment.address.pincode)
                serializer.data['address'].update(pincode_serializer.data)
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))

    def post(self, request):
        """
        This creates or updates an appointment schedule.

        :param request: http request method that contains the user and appointment details.
        :return: success response on successful creation or updation.
        """
        with transaction.atomic():
            is_succesful, data = utils.generate_address(request.data.get('address'))
            if not is_succesful:
                return api_utils.response({"field": "address"}, status.HTTP_400_BAD_REQUEST,
                                          constants.INCORRECT_PINCODE_SET)
            address_serializer = serializers.AddressSerializer(data=data)
            if address_serializer.is_valid():
                address = address_serializer.save()
                models.AppointmentDetails.objects.update_or_create(
                        user=request.user, defaults={"address_id": address.id, "date": request.data.get('date'),
                                                     "time": request.data.get('time')})
                return api_utils.response({"message": constants.SUCCESS})
            else:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST,
                                          generate_error_message(address_serializer.errors))


class SetProcessChoice(APIView):
    """
    This has methods to set the process choice type.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        This sets the process choice field.
        :param request: contains the process choice type.
        :return: success response on successful setting of the process choice field of the pertinent user.
        """
        serializer = serializers.SetProcessChoiceSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_utils.response({"message": constants.SUCCESS})
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class GetSignature(APIView):
    """
    Displays the signature of the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request: contains the user id.
        :return: Displays the signature of the user
        """
        serializer = serializers.SaveSignatureSerializer(request.user)
        if serializer.is_valid:
            return api_utils.response(serializer.data)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class InvestorAccountInfoGet(APIView):
    """
    API to return users account info and bank detials
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Returns user's account info
        :param request:
        :return:
        """
        try:
            investor_bank_details = models.InvestorBankDetails.objects.get(user=request.user)
        except models.InvestorBankDetails.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.INVESTOR_ACCOUNT_NOT_PRESENT},
                                      status.HTTP_404_NOT_FOUND, constants.INVESTOR_ACCOUNT_NOT_PRESENT)
        serializer = serializers.InvestorBankInfoGetSerializer(investor_bank_details)
        return api_utils.response(serializer.data)


class InvestorAccountInfoPost(APIView):
    """
    API to post investor account info
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        ifsc_code = request.data.get(constants.IFSC_CODE)
        try:
            bank_object = external_models.BankDetails.objects.get(ifsc_code=ifsc_code)
        except external_models.BankDetails.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.INCORRECT_IFSC_CODE},
                                      status.HTTP_404_NOT_FOUND, constants.INCORRECT_IFSC_CODE)
        try:
            investor_info_object = models.InvestorBankDetails.objects.get(user=request.user)
            serializer = serializers.InvestorBankInfoPostSerializer(investor_info_object, data=request.data)
        except models.InvestorBankDetails.DoesNotExist:
            serializer = serializers.InvestorBankInfoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ifsc_code=bank_object, user=request.user)
            utils.set_user_check_attributes(request.user, 'is_bank_info')
            return api_utils.response({"message": constants.SUCCESS})
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class CheckEmailPhone(APIView):
    """
    API to check if an email or phone_number is already present
    """
    def post(self, request):
        """
        :param request:
        :return:
        """
        email = request.data.get('email', None)
        phone_number = request.data.get('phone_number', None)
        if email is None and phone_number is None:
            return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.EMAIL_PHONE_NOT_PROVIDED)
        elif email is not None:
            try:
                models.User.objects.get(email__iexact=email, email_verified=True)
            except models.User.DoesNotExist:
                return api_utils.response({"message": constants.EMAIL_NOT_PRESENT}, status.HTTP_200_OK)
            return api_utils.response({"message": constants.EMAIL_ALREADY_PRESENT}, status.HTTP_200_OK)
        elif phone_number is not None:
            try:
                models.User.objects.get(phone_number=phone_number, phone_number_verified=True)
            except models.User.DoesNotExist:
                return api_utils.response({"message": constants.PHONE_NOT_PRESENT}, status.HTTP_200_OK)
            return api_utils.response({"message": constants.PHONE_ALREADY_PRESENT}, status.HTTP_200_OK)


class VerifyForgotPasswordOTP(APIView):
    """
    API to verify OTP when user forgets password
    """

    def post(self, request):
        """
        :param request:
        :return:
        """
        serializer = serializers.ForgotPasswordCheckOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = models.User.objects.get(email=serializer.data.get('email'))
            except models.User.DoesNotExist:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.USER_WITH_EMAIL_NOT_PRESENT)
            try:
                verification_object = models.VerificationSMSCode.objects.get(user=user)
            except models.VerificationSMSCode.DoesNotExist:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, constants.VERIFICATION_CODE_NOT_PRESENT)
            if verification_object.sms_code == serializer.data.get('otp'):
                applicant_name = investor_info_check(request.user)
                helpers.send_reset_email(user=user,applicant_name=applicant_name, use_https=settings.USE_HTTPS)
                user.email_verified = True
                user.save()
                return api_utils.response({"message": constants.RESET_EMAIL_SENT})
            return api_utils.response({"message": constants.INCORRECT_SMS_CODE}, status.HTTP_404_NOT_FOUND,
                                      constants.INCORRECT_SMS_CODE)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))
    

class ChangePhoneNumber(APIView):
    """
    Sends OTP to user who want to change their phone number
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:  Sends OTP to user who want to change their phone number
        """
        user = request.user
        if user.is_active:
            serializer = serializers.PhoneNumberSerializer(request.user, data=request.data)
            if serializer.is_valid():
                sms_code = utils.get_sms_verification_code(user)
                phone_number = int(serializer.validated_data.get('phone_number'))
                sms_code_sent = api.send_sms(constants.RESET_PHONE_NUMBER_OTP.format(sms_code), phone_number)
                models.UserChangedPhoneNumber.objects.update_or_create(user=user, defaults={'sms_code': sms_code, 'phone_number': str(phone_number)})
                return api_utils.response({"message": constants.VERIFY_SMS_SENT, "sms_code_sent": sms_code_sent})
                # return api_utils.response({"message": constants.VERIFY_SMS_NOT_SENT, "sms_code_sent": sms_code_sent})
            else:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))
        else:
            return api_utils.response({"message": constants.NON_ACTIVE_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                          constants.NON_ACTIVE_USER_ERROR)


class ConfirmChangeInPhoneNumber(APIView):
    """
    Changes the user's phone number once he enters correct OTP
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        :param request:
        Changes the user's phone number
        """
        try:
            verification_object = models.UserChangedPhoneNumber.objects.get(user=request.user)
            if verification_object.sms_code == request.data.get('sms_code', 00000):
                old_phone_number = request.user.phone_number
                request.user.phone_number = verification_object.phone_number
                request.user.phone_number_verified = True
                request.user.save()
                verification_object.delete()
                if request.user.email_verified:
                    applicant_name = investor_info_check(request.user)
                    helpers.send_phone_number_change_email(user_email=request.user.email,applicant_name=applicant_name, previous_number=old_phone_number[-5:], new_number=verification_object.phone_number[-5:], use_https=settings.USE_HTTPS)
                return api_utils.response({"message": constants.PHONE_VERIFIED})
            else:
                return api_utils.response({"message": constants.INCORRECT_SMS_CODE}, status.HTTP_404_NOT_FOUND,
                                          constants.INCORRECT_SMS_CODE)
        except models.UserChangedPhoneNumber.DoesNotExist:
            return api_utils.response({"message": constants.NON_EXISTENT_USER_ERROR}, status.HTTP_404_NOT_FOUND,
                                      constants.NON_EXISTENT_USER_ERROR)


class VideoUpload(APIView):
    """
    To save user video and its thumbnail
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        serializer = serializers.SaveUserVideoSerializer(data=request.data)
        if serializer.is_valid():
            request.user.user_video = request.FILES.get("user_video", None)
            request.user.user_video_thumbnail = request.FILES.get("user_video_thumbnail", None)
            request.user.save()
            return api_utils.response({"message": constants.USER_VIDEO_SAVED,
                                       "user_video_thumbnail": request.user.user_video_thumbnail.url,
                                       "user_video": request.user.user_video.url}, status.HTTP_200_OK)
        return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))


class VideoGet(APIView):
    """
    API to get user video and user video thumbnail
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        serializer = serializers.SaveUserVideoSerializer(request.user)
        if serializer.is_valid:
            response = serializer.data
            response.update({"has_uploaded": False})
            response.update({"name": request.user.investorinfo.applicant_name})
            if serializer.data.get("user_video") is not None and serializer.data.get("user_video_thumbnail") is not None:
                response.update({"has_uploaded": True})
            return api_utils.response(response)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST, generate_error_message(serializer.errors))


class DeleteUser(APIView):
    """
    API to delete user by phonenumber
    """

    def get(self, request):
        """
        :param request:
        :return:
        """
        models.User.objects.get(email=request.query_params.get('email')).delete()
        return api_utils.response({"success":"ok"})


class LockVault(APIView):
    """
    API to lock vault for a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        
        vaultLocked = request.user.vault_locked 
        request.user.vault_locked = True
        request.user.save()
        if vaultLocked == False:
            
            investor = models.InvestorInfo.objects.get(user=request.user)
                
            if investor.applicant_name is not None:
                user_name = investor.applicant_name
            else:
                user_name = request.user.email
                    
            helpers.send_vault_completion_email_user(request.user, user_name,request.user.email, use_https=settings.USE_HTTPS)

        return api_utils.response({constants.MESSAGE:constants.SUCCESS})



class GoogleLogin(APIView):
    """
    Google Register views , User already Registered through google and trying to login through google  ## 1
    """
    def post(self, request, format=None):
        
        serializer = serializers.SocialUserRegisterSerializer(data=request.data)
        email = serializer.initial_data.get("email")
        
        auth_code = request.data['auth_code']
        

        kwargs = {'email': email, 'access_token': ''}

        user,user_detail = utils.check_existing_user_email(**kwargs)

        if user_detail == constants.GOOGLE_LOGIN_EXIST_GOOGLE_USER:
            ## registered Through Google  --> login Details
            user_status = constants.GOOGLE_LOGIN_EXIST_GOOGLE_USER
            
            logger = logging.getLogger('django.debug')
            logger.debug("Google Login: User with email id" + email)
        
        elif user_detail == constants.GOOGLE_LOGIN_EXIST_FINASKUS_USER:
            ## registered Through Finaskus App  --> it has to be merge with google
            if not user.email_verified and not user.phone_number_verified:
                user_status = constants.GOOGLE_REGISTER
                login_error = constants.LOGIN_ERROR_1
                return api_utils.response({"res":{},"user_status":user_status})
                
            else:
                user_status = constants.GOOGLE_LOGIN_EXIST_FINASKUS_USER
                return api_utils.response({"res":{},"user_status":user_status})
           
        else:
            ## Not yet Registered 
            user_status = constants.GOOGLE_REGISTER
            login_error = constants.LOGIN_ERROR_1
            return api_utils.response({"res":{},"user_status":user_status})
        
        if not user.phone_number_verified and not user.email_verified:
            login_error = constants.LOGIN_ERROR_2
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND,
                                      constants.PHONE_AND_EMAIL_NOT_VERIFIED)
            
        serializer = serializers.SocialUserRegisterSerializer(user)
        if serializer.is_valid:
            if user.is_active:
                if user_status == constants.GOOGLE_LOGIN_EXIST_GOOGLE_USER:
                    
                    access_token = helpers.convert_auth_to_access_token(auth_code)
                    
                    if access_token is not None:
                        convert_token = helpers.convert_social_access_token(access_token)
                        
                        return api_utils.response({"res":{"user": serializer.data,
                                                    "tokens":convert_token,
                                                    "assess": core_utils.get_assess_answer(user),
                                                    "plan": core_utils.get_plan_answers(user),
                                                    "retirement": core_utils.get_category_answers(user, "retirement"),
                                                    "tax": core_utils.get_category_answers(user, "tax"),
                                                    "invest": core_utils.get_category_answers(user, "invest"),
                                                    "education": core_utils.get_category_answers(user, "education"),
                                                    "wedding": core_utils.get_category_answers(user, "wedding"),
                                                    "property": core_utils.get_category_answers(user, "property"),
                                                    "event": core_utils.get_category_answers(user, "event")},
                                                    "user_status":user_status
                                                   })
                    else:
                        return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": "login_error"},
                                                    status.HTTP_401_UNAUTHORIZED,
                                                    constants.GOOGLE_LOGIN_ERROR)  
            else:
                login_error = constants.LOGIN_ERROR_6
                return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                          status.HTTP_404_NOT_FOUND,
                                          constants.NON_ACTIVE_USER_ERROR)
        else:
            login_error = constants.LOGIN_ERROR_0
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                      status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))
            
            
class GoogleRegister(APIView):
    """
    Google Register views , User not registered through either finaskus or google   ## 3
    """

    def post(self, request, format=None):

        user = None
        serializer = serializers.SocialUserRegisterSerializer(data=request.data)
        email = serializer.initial_data.get("email")
        phone = serializer.initial_data.get("phone_number")
        kwargs = {'email': email, 'phone_number': phone, 'password': ''}
        
        logger = logging.getLogger('django.debug')
        logger.debug("Google Register: User with email id" + email)
        
        utils.check_existing_user(**kwargs)
            
        phone_exist = utils.phone_number_check(phone)
        
        if phone_exist is None:     
            auth_code = request.POST.get('auth_code', False)

            access_token = helpers.convert_auth_to_access_token(auth_code)
             
            if access_token is not None:
                try:
                    convert_token = helpers.convert_social_access_token(access_token)
                except:
                    return api_utils.response({}, status.HTTP_404_NOT_FOUND,
                                                  constants.GOOGLE_LOGIN_ERROR)
                
                user = utils.get_social_user(email)
                    
                if user is not None:
                    user.username = email
                    user.phone_number = phone
                    user.email_verified = True
                      
                    if request.data['image'] is not None:
                        url = request.data['image']
                        ext = url.split('.')[-1]
                        user.image.save('{0}.{1}'.format('image', ext),ContentFile(urllib2.urlopen(url).read()),save=False)
                        user.identity_info_image.save('{0}.{1}'.format('image', ext),ContentFile(urllib2.urlopen(url).read()),save=False)
                    
                    user.save()
                    serializer = serializers.SocialUserRegisterSerializer(user, data=request.data)
                    if serializer.is_valid():
                        user_response = dict(serializer.data)
                        user_response['risk_score'], user_response['name'] = None, ""
                        
                        sms_code = utils.get_sms_verification_code(user)
                            # TODO : add provisions to add country code?
                        send_sms_thread = threading.Thread(target=api.send_sms, args=(constants.OTP.format(sms_code), int(phone),))
                        send_sms_thread.start()           
                            #sms_code_sent = api.send_sms(constants.OTP.format(sms_code), int(phone))            
                        return api_utils.response({"user": user_response, 
                                                       "tokens": convert_token,
                                                       "assess": core_utils.get_assess_answer(user),
                                                       "plan": core_utils.get_plan_answers(user),
                                                       "retirement": core_utils.get_category_answers(user, "retirement"),
                                                       "tax": core_utils.get_category_answers(user, "tax"),
                                                       "invest": core_utils.get_invest_answers(user),
                                                       "education": core_utils.get_category_answers(user, "education"),
                                                       "wedding": core_utils.get_category_answers(user, "wedding"),
                                                       "property": core_utils.get_category_answers(user, "property"),
                                                       "event": core_utils.get_category_answers(user, "event"),
                                                       })
                    else:
                        return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))
                else:
                    return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": "login_error"}, status.HTTP_401_UNAUTHORIZED,
                                                  constants.GOOGLE_LOGIN_ERROR) 
            else:
                return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": "login_error"}, status.HTTP_401_UNAUTHORIZED,     
                                                  constants.GOOGLE_LOGIN_ERROR) 
        else:
                return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": "login_error"}, status.HTTP_404_NOT_FOUND,
                                               constants.PHONE_EXISTS)



class GoogleRegisterExistingUser(APIView):
    """
    Google Register views , User have registered through finaskus app but through google its first time ##4
    """
    def post(self, request, *args, **kwargs):
        serializer = serializers.SocialUserRegisterSerializer(data=request.data)
        provider = 'google-oauth2'
        email = request.data['email']
        password = request.data['password']
        auth_code = request.POST.get('auth_code', False)
        
        logger = logging.getLogger('django.debug')
        logger.debug("Google account merge: User with email id" + email)
        
        user = utils.get_social_user(email)
        if user.check_password(password):
            access_token = helpers.convert_auth_to_access_token(auth_code)
            
            if access_token is not None:
        
                if user is not None:
                    if not user.phone_number_verified and not user.email_verified:
                        login_error = constants.LOGIN_ERROR_2
                        return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_404_NOT_FOUND,
                                                  constants.PHONE_AND_EMAIL_NOT_VERIFIED)
                    
                    #authed_user = request.user if not request.user.is_anonymous() else None
                    authed_user = user
                    strategy = load_strategy(request)
                    backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
                    if isinstance(backend, BaseOAuth1):
                        token = {
                            'oauth_token': access_token,
                            'oauth_token_secret': '',
                        }
                    elif isinstance(backend, BaseOAuth2):
                        #token = request.POST.get('access_token', False)
                        token = access_token
            
                    try:
                        user = backend.do_auth(token, user=authed_user)
                        convert_token = helpers.convert_social_access_token(access_token)

                    except AuthAlreadyAssociated:
                        # You can't associate a social account with more than user
                        return Response({"errors": "That social media account is already in use"},
                                        status=status.HTTP_400_BAD_REQUEST)
            
                    if user and user.is_active:
                        auth_created = user.social_auth.get(provider=provider)
                        if not auth_created.extra_data['access_token']:
                            auth_created.extra_data['access_token'] = token
                            auth_created.save()
    
                        serializer = serializers.SocialUserRegisterSerializer(user)
                        if serializer.is_valid:
                            user_response = dict(serializer.data)
                            return api_utils.response({"user": user_response, 
                                                           "tokens": convert_token,
                                                           "assess": core_utils.get_assess_answer(user),
                                                           "plan": core_utils.get_plan_answers(user),
                                                           "retirement": core_utils.get_category_answers(user, "retirement"),
                                                           "tax": core_utils.get_category_answers(user, "tax"),
                                                           "invest": core_utils.get_invest_answers(user),
                                                           "education": core_utils.get_category_answers(user, "education"),
                                                           "wedding": core_utils.get_category_answers(user, "wedding"),
                                                           "property": core_utils.get_category_answers(user, "property"),
                                                           "event": core_utils.get_category_answers(user, "event"),
                                                           })
                              
                        else:
                            login_error = constants.LOGIN_ERROR_5
                            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_404_NOT_FOUND,
                                                  constants.LOGIN_ERROR)
                    else:
                        login_error = constants.LOGIN_ERROR_5
                        return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_404_NOT_FOUND,
                                                  constants.LOGIN_ERROR)
                else:
                    login_error = constants.LOGIN_ERROR_5
                    return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_404_NOT_FOUND,
                                                  constants.LOGIN_ERROR)
            else:
                login_error = constants.LOGIN_ERROR_5
                return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_401_UNAUTHORIZED,
                                                  constants.GOOGLE_LOGIN_ERROR) 
        else:
            login_error = constants.LOGIN_ERROR_5
            return api_utils.response({"message": constants.UNABLE_TO_LOGIN, "login_error": login_error},
                                                  status.HTTP_404_NOT_FOUND,
                                                  constants.LOGIN_ERROR)   