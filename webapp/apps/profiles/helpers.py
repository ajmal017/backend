"""
To make structure of code more organised. We are keeping all those functions that don't involve model queries here


"""
from django.conf import settings
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import requests
from requests.auth import HTTPBasicAuth

from . import constants as profile_constants
import logging

def unique_filename(path, context):
    if path and context:
        newPath = path + "/" + str(context)
        return newPath
    return path

def make_dictionary(question_value, answer_text_value, answer_metadata_value):
    """
    Makes a dictionary in required format
    :param question_value: value for key 'question_id'
    :param answer_text_value: value for key 'text'
    :param answer_metadata_value: value for key 'metadata'
    :return: returns a dictionary in format required
    """
    dictionary_to_append = {
        'question_id': question_value,
        'answer': [{'text': answer_text_value, 'metadata': answer_metadata_value}]}
    return dictionary_to_append


def get_access_token(user, password):
    """
    :return: The json formatted data to be returned along with access_token
    """
    data = {'grant_type': 'password', 'username': user.username, 'password': password}
    auth = HTTPBasicAuth(settings.CLIENT_ID, settings.CLIENT_SECRET)
    response = requests.post(settings.BASE_URL + '/o/token/', auth=auth, data=data)
    responseJSON = response.json()
    if not responseJSON.get('access_token'):
        logger = logging.getLogger('django.error')
        logger.error("Profiles: access_token: Access token failed for user with id: " + user.id)
            
    return responseJSON


def send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    logger = logging.getLogger('django.info')

    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    if email_template_name is not None:
        body = loader.render_to_string(email_template_name, context)
    else:
        body = ''
    if isinstance(to_email, list):
        email_message = EmailMultiAlternatives(subject, body, from_email, to_email)
    else:
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
        logger.info("send_email: to: " + to_email + " template: " + html_email_template_name)


    email_message.send()


def send_email_change_notify_to_old_email(old_email, new_email, subject_template_name='notify_old_email/subject.txt',
                                          email_template_name=None, use_https=False, from_email=None,
                                          html_email_template_name='notify_old_email/email.html'):
    """
    Sends email to old email of user notifying him/her of email change request

    :param old_email:the old email of user to which email id change mail has to be sent
    :param new_email:the new email of user
    :param subject_template_name: file containing subject of email
    :param email_template_name: file containing body of email
    :param use_https: boolean to whether use https or not
    :param from_email:
    :param html_email_template_name:
    :return:
    """
    context = {
        'old_email': old_email,
        'new_email': new_email,
        'domain': settings.SITE_BASE_URL,
        'site_name': profile_constants.SITE_NAME,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, old_email,
              html_email_template_name=html_email_template_name)


def send_bse_registration_email(user_email_list, domain_override=None,
                                subject_template_name='bse_register/subject.txt',
                                email_template_name='bse_register/bse_register_email.html', use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name=None, extra_email_context=None):
    """
     Sends an email of list of user emil whose bse registration has to be done
    """
    context = {
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'user_list': user_email_list,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)


def send_kra_verified_email(user, domain_override=None, subject_template_name='kra_verified/subject.txt',
                            email_template_name='kra_verified/kra_verified_email.html', use_https=False,
                            token_generator=default_token_generator, from_email=None, request=None,
                            html_email_template_name=None, extra_email_context=None):
    """
    Sends email when a users kra is verified
    """
    context = {
        'user': user,
        'email': user.email,
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)

    if user.vault_locked:
        send_mail("vault_completion/user_kyc_subject.txt", None, context, from_email, user.email,
              html_email_template_name="vault_completion/vault_complete_kyc_verified.html")
        

def send_kyc_verification_email(user_email_list, domain_override=None,
                                subject_template_name='kyc_verify_pending/subject.txt',
                                email_template_name='kyc_verify_pending/kyc_verify_email.html', use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name=None, extra_email_context=None):
    """
     Sends an email of list of user emil whose kyc is pending
    """
    context = {
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'user_list': user_email_list,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)

def send_vault_completion_email_user(user, user_email, domain_override=None,
                                subject_template_name='vault_completion/user_account_active.txt',
                                email_template_name=None, use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name='vault_completion/vault_complete_account_active.html', extra_email_context=None):
    """
     Sends an email when vault is completed to user.
    """
    context = {
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'user_email': user_email,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    send_vault_completion_email(user, user_email, use_https=settings.USE_HTTPS)
    
    if user.get_kra_verified() == True:
        send_mail(subject_template_name, email_template_name, context, from_email, user.email,
              html_email_template_name=html_email_template_name)
    else:
        if user.user_video is not None:
            send_mail('vault_completion/user_nonkyc_subject.txt', email_template_name, context, from_email, user.email,
              html_email_template_name='vault_completion/vault_complete_kyc_unverified.html')

    
def send_vault_completion_email(user, user_email, domain_override=None,
                                subject_template_name='vault_completion/subject.txt',
                                email_template_name='vault_completion/vault_completed_email.html', use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name=None, extra_email_context=None):
    """
     Sends an email when vault is completed.
    """
    context = {
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'user_email': user_email,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)
    

def send_transaction_completed_email(order_detail, domain_override=None, subject_template_name='transaction/subject.txt',
                                     email_template_name='transaction/transaction_completed.html', use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name='transaction/user-confirm-pay.html', extra_email_context=None):
    """
    Sends email when a transaction is completed
    """
    context = {
        'order_detail': order_detail,
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=None)
    
    send_mail('transaction/user-subject.txt', None, context, from_email, order_detail.user.email,
              html_email_template_name=html_email_template_name)
    


def send_reset_email(user, domain_override=None, subject_template_name='registration/password_reset_request_subject.txt',
                     email_template_name=None, use_https=False,
                     token_generator=default_token_generator, from_email=None, request=None,
                     html_email_template_name='registration/password_reset_email.html', extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        context = {
            'email': user.email,
            'domain': settings.SITE_BASE_URL,
            'site_name': "Finaskus",
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        send_mail(subject_template_name, email_template_name, context, from_email, user.email,
                  html_email_template_name=html_email_template_name)


def send_verify_email(user, code, domain_override=None, subject_template_name='verify_email/verify_email_subject.txt',
                      email_template_name=None, use_https=False,
                      token_generator=default_token_generator, from_email=None, request=None,
                      html_email_template_name='verify_email/verify_email.html', extra_email_context=None):
    """

    :param user: user whose email is to be verified
    :param code: an alphanumeric code of length 50
    :param domain_override:
    :param subject_template_name: file containing subject of email
    :param email_template_name: file containing body of email
    :param use_https: boolean to whether use https or not
    :param token_generator:
    :param from_email:
    :param request:
    :param html_email_template_name:
    :param extra_email_context:
    :return:
    """
    context = {
        'email': user.email,
        'domain': settings.SITE_BASE_URL,
        'site_name': profile_constants.SITE_NAME,
        'user': user,
        'token': code,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, user.email,
              html_email_template_name=html_email_template_name)


def send_mail_with_attachment(subject_template_name, email_template_name, context, from_email, to_email,
                              email_attachment, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    attachment = open(email_attachment, 'rb')
    email_message.attach(email_attachment, attachment.read(),'application/pdf')
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()


def send_phone_number_change_email(user_email, previous_number, new_number, domain_override=None,
                                subject_template_name='registration/phone_number_reset.txt',
                                email_template_name=None, use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name='registration/phone_number_reset.html', extra_email_context=None):
    """
     Sends an email when user has successfully changed his phone number.
    """
    context = {
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'user_email': user_email,
        'previous_number': previous_number,
        'new_number': new_number,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, user_email,
              html_email_template_name=html_email_template_name)


def send_redeem_completed_email(redeem_detail, domain_override=None, subject_template_name='transaction/subject.txt',
                                     email_template_name='transaction/redeem_completed.html', use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name=None, extra_email_context=None):
    """
    Sends email when a transaction is completed
    """
    context = {
        'redeem_detail': redeem_detail,
        'domain': settings.SITE_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)
