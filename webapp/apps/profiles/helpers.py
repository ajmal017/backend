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
import copy
from django.db.models import Sum
import datetime
from oauth2_provider.models import AccessToken


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

def update_access_token_expiry(user, access_token, is_web):
    if is_web is True:
        logger = logging.getLogger('django.debug')

        expires = datetime.datetime.now() + datetime.timedelta(seconds=settings.WEB_ACCESS_TOKEN_EXPIRE_SECONDS)
        access_tokens = AccessToken.objects.filter(user=user, token=access_token, expires__gt=expires)
        if len(access_tokens) > 1:
            logger.debug("More than one access token: " + str(access_token))
        elif len(access_tokens) == 1:
            logger.debug("Found one access token: " + str(access_token) + " expires: " + str(access_tokens[0].expires) + " new expires: " + str(expires))
            AccessToken.objects.filter(id=access_tokens[0].id).update(expires=expires)

def get_access_token(user, password, is_web=False):
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
    else:
        logger = logging.getLogger('django.debug')
        logger.debug(responseJSON)
        update_access_token_expiry(user, responseJSON.get('access_token'), is_web)
            
    return responseJSON



def convert_social_access_token(user, access_token, is_web=False):
    """
     Return : Converted access token to application
    """
    data = {'grant_type':'convert_token','backend':'google-oauth2','token':access_token,'client_id':settings.CLIENT_ID,'client_secret':settings.CLIENT_SECRET}
    response = requests.post(settings.BASE_URL + '/auth/convert-token/', data=data)
    responseJSON = response.json()
    if not responseJSON.get('access_token'):
        logger = logging.getLogger('django.error')
        logger.error("Profiles: access_token: Access token failed for user with id: ")      
    else:
        logger = logging.getLogger('django.debug')
        logger.debug(responseJSON)
        update_access_token_expiry(user, responseJSON.get('access_token'), is_web)
    return responseJSON


def convert_auth_to_access_token(auth_code, is_web):
    redirect_uri = ''
    if is_web:
        redirect_uri = 'postmessage'
    data = {'grant_type':'authorization_code','code':auth_code,'client_id':settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,'client_secret':settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri':redirect_uri}
    response = requests.post(settings.GOOGLE_PLUS_AUTH_URL, data=data)
    responseJSON = response.json()
    if responseJSON.get('access_token'):     
        return responseJSON['access_token']
    else:
        return None

def send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    logger = logging.getLogger('django.debug')

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
        logger.debug("send_email: to: " + to_email + " template: " + html_email_template_name)


    email_message.send()


def send_email_change_notify_to_old_email(old_email,applicant_name, new_email, subject_template_name='notify_old_email/subject.txt',
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
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = old_email
    context = {
        'old_email': old_email,
        'new_email': new_email,
        'user_name':userName,
        'domain': settings.SITE_API_BASE_URL,
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
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'user_list': user_email_list,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)


def send_kra_verified_email(user,applicant_name, domain_override=None, subject_template_name='kra_verified/subject.txt',
                            email_template_name='kra_verified/kra_verified_email.html', use_https=False,
                            token_generator=default_token_generator, from_email=None, request=None,
                            html_email_template_name=None, extra_email_context=None):
    """
    Sends email when a users kra is verified
    """
    
    
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = user.email

    
       
    """
    check for applicant name exist or not
    """
    context = {
        'user': user,
        'email': user.email,
        'user_name':userName,
        'domain': settings.SITE_API_BASE_URL,
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
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'user_list': user_email_list,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)

def send_vault_completion_email_user(user, applicant_name,user_email, domain_override=None,
                                subject_template_name='vault_completion/user_account_active.txt',
                                email_template_name=None, use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name='vault_completion/vault_complete_account_active.html', extra_email_context=None):
    """
     Sends an email when vault is completed to user.
    """
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = user.email
    context = {
        'user_name':userName,
        'domain': settings.SITE_API_BASE_URL,
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
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'user_email': user_email,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)
    

def send_transaction_completed_email(order_detail_lumpsum,applicant_name,user_email, payment_completed, inlinePayment, 
                                     domain_override=None, subject_template_name='transaction/subject.txt',
                                     email_template_name='transaction/transaction_completed.html', use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name='transaction/user-confirm-pay.html', extra_email_context=None):
    """
    Sends email when a transaction is completed
    """
    if applicant_name is not None:
        user_name = applicant_name.title()
    else:
        user_name = user_email
    
    context = {   
        'order_detail_lumpsum':order_detail_lumpsum,
        'user_name':user_name,
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    
    if payment_completed == True:
        html_email_template_name='transaction/user-confirm-payment-complete.html'
        
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=None)
    
    
    send_mail('transaction/user-subject.txt', None, context, from_email, user_email,
              html_email_template_name=html_email_template_name)


def send_transaction_change_email(first_order,order_detail,applicant_name,user,email_attachment,attachment_error,
                                  domain_override=None, subject_template_name='transaction/subject.txt',
                                     email_template_name='transaction/transaction_status_change.html', use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,extra_email_context=None):
    
    
    """
    Template changes according to mandate status of the user 
    """ 
    if first_order == True:      
        if order_detail.bank_mandate and order_detail.bank_mandate.mandate_status == "0":   
            if all(sips < 1 for sips in order_detail.all_sips) & any(lumpsums > 0 for lumpsums in order_detail.all_lumpsums):
                html_email_template_name='transaction/user-confirm-status-change.html'
                subject_name = 'transaction/user-status-change-subject.txt'
                email_attachment = None
                attachment_error = None
            else:
                html_email_template_name='transaction/user-confirm-status-change-sip.html'
                subject_name = 'transaction/user-mandate-subject.txt'
        else:
            html_email_template_name='transaction/user-confirm-status-change-ongoing.html'
            subject_name = 'transaction/user-status-change-subject.txt'
    else:
        html_email_template_name='transaction/user-confirm-following-sip.html'
        subject_name = 'transaction/user-status-change-subject.txt'
    
    list1 = zip(order_detail.fund_order_list,order_detail.nav_list)
    
    if applicant_name is not None:
        user_name = applicant_name.title()
    else:
        user_name = user.email
        
    month = datetime.datetime.strftime(order_detail.created_at, '%B')    

    context = {
        'order_detail':list1,        
        'user_name':user_name,
        'transaction_detail':order_detail,
        'sip_allotment_date':order_detail.fund_order_items.first().allotment_date,
        'month':month,
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    if order_detail.unit_alloted == True and attachment_error == None:
        subject = loader.render_to_string(subject_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(html_email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [user.email], bcc=[settings.DEFAULT_TO_EMAIL,settings.DEFAULT_FROM_EMAIL])
        if order_detail.bank_mandate and order_detail.bank_mandate.mandate_status == "0" and email_attachment is not None:
            attachment = open(email_attachment, 'rb')
            email_message.attach('bank_mandate.pdf', attachment.read(),'application/pdf')
            order_detail.bank_mandate.mandate_status = 1
            order_detail.bank_mandate.save()
        email_message.attach_alternative(body, 'text/html')
        email_message.send()
        return "success"
    else:
        send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=None)
        return "Failed"
    
    

def send_reset_email(user,applicant_name,domain_override=None, subject_template_name='registration/password_reset_request_subject.txt',
                     email_template_name=None, use_https=False,
                     token_generator=default_token_generator, from_email=None, request=None,
                     html_email_template_name='registration/password_reset_email.html', extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        if applicant_name is not None:
            user_name = applicant_name.title()
        else:
            user_name=user.email
            
        context = {
            'email': user.email,
            'user_name':user_name,
            'domain': settings.SITE_API_BASE_URL,
            'site_name': "Finaskus",
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        send_mail(subject_template_name, email_template_name, context, from_email, user.email,
                  html_email_template_name=html_email_template_name)


def send_verify_email(user, applicant_name, code, domain_override=None, subject_template_name='verify_email/verify_email_subject.txt',
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
    if applicant_name is not None:
        user_name = applicant_name.title()
    else:
        user_name=user.email
    
    
    context = {
        'user_name':user_name,      
        'email': user.email,
        'domain': settings.SITE_API_BASE_URL,
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


def send_phone_number_change_email(user_email,applicant_name,previous_number, new_number, domain_override=None,
                                subject_template_name='registration/phone_number_reset.txt',
                                email_template_name=None, use_https=False,
                                token_generator=default_token_generator, from_email=None, request=None,
                                html_email_template_name='registration/phone_number_reset.html', extra_email_context=None):
    """
     Sends an email when user has successfully changed his phone number.
    """
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = user_email
       
    context = {
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'user_email': user_email,
        'user_name':userName,
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
        'domain': settings.SITE_API_BASE_URL,
        'site_name': "Finaskus",
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=html_email_template_name)
    


def send_mail_reminder_next_sip(fund_order_items,target_date,total_sip,bank_details,applicant_name,user,domain_override=None, subject_template_name='transaction/sip-reminder-subject.txt',
                                     email_template_name=None, use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name='transaction/sip-reminder.html', extra_email_context=None):
                   
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = user.email
        
    if bank_details is not None and bank_details.account_number is not None:
        x = bank_details.account_number
        y = list(x)
        y.reverse()
        index = 0
        while index < len(y):
            if index > 3:
                y[index] = 'X'
            index = index + 1
                
        y.reverse() 
        bank_account_number = ''.join(y)
    else:
        bank_account_number = None
       
    context = {     
              'domain': settings.SITE_API_BASE_URL,
              'site_name': "Finaskus",
              'user': user,
              'bank_details':bank_details,
              'bank_account_number':bank_account_number,
              'total_sip':total_sip,
              'user_name':userName,
              'fund_order_items':fund_order_items,
              'next_allotment_date':target_date,
              'protocol': 'https' if use_https else 'http',
               }
    send_mail(subject_template_name, email_template_name, context, from_email, user.email,
                          html_email_template_name=html_email_template_name) 
    return True
                    
def send_mail_weekly_portfolio(portfolio_details,user,applicant_name,domain_override=None, subject_template_name='transaction/weekly-portfolio-subject.txt',
                                     email_template_name=None, use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name='transaction/weekly_portfolio_snapshot.html', extra_email_context=None):                
    if applicant_name is not None:
        userName = applicant_name.title()
    else:
        userName = user.email
    context = {     
             'domain': settings.SITE_API_BASE_URL,
             'site_name': "Finaskus",
             'user': user,
             'user_name':userName,
             'portfolio_details':portfolio_details,
             'protocol': 'https' if use_https else 'http',
               }
    send_mail(subject_template_name, email_template_name, context, from_email, user.email,
                          html_email_template_name=html_email_template_name) 
    

def send_mail_admin_next_sip(users,current_date,target_date, domain_override=None, subject_template_name='transaction/sip-reminder-subject.txt',
                                     email_template_name='transaction/sip_reminder_users_list.html', use_https=False,
                                     token_generator=default_token_generator, from_email=None,
                                     request=None,html_email_template_name=None, extra_email_context=None):
    context = {     
             'domain': settings.SITE_API_BASE_URL,
             'site_name': "Finaskus",
             'users': users,
             'current_date':current_date,
             'target_date':target_date,
             'protocol': 'https' if use_https else 'http',
               }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=None)  
    
def send_user_video_upload_email(user,domain_override=None, subject_template_name='user_video/subject.txt',
                                    email_template_name='user_video/user_video_email.html', use_https=False,
                                    token_generator=default_token_generator, from_email=None, request=None,
                                    html_email_template_name=None, extra_email_context=None):
    
    context = {     
             'domain': settings.SITE_API_BASE_URL,
             'site_name': "Finaskus",
             'user': user,
             'protocol': 'https' if use_https else 'http',
               }
    send_mail(subject_template_name, email_template_name, context, from_email, settings.DEFAULT_TO_EMAIL,
              html_email_template_name=None)    