from django.conf import settings
from django.db.models import Sum, F

from core import models as core_models
from core import constants
from profiles import constants as cons
from profiles import models as profile_models
from external_api import cvl 
from webapp.apps import random_with_N_digits
from . import helpers
import logging
import social.apps.django_app.default.models as social_model

from datetime import datetime
from numpy.ma.core import remainder

import io
from io import StringIO
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage
from PIL import Image

def get_answers(user_id):
    """
    Gets a list of answers by user(user_id) according to category(question_for) and returns them in a format -

    user_answers ={         //user_answers is a dictionary with keys 'tax','retirement' etc.
        'tax':[            //value of key 'tax' is a list of dictionaries with keys 'question_id' and 'answers'
            {
                'question_id': id_value,
                'answers': [        //value of key 'answers' is a list of dictionaries with keys 'text' and 'metadata'
                    {
                        'text': text_value,     //text_value =option_id for radio button
                                                            =user answer in case of multi-text question or text question
                        'metadata': metadata_value      //metadata will have order in case of multi-text
                    },
                    //answer will have just one element in case of radio and text question
                    //answer might have more than one elements in case of multi-text question
                    {}
                ]
            }
            .......same for each question in tax category
        ]
        'retirement':[
            {}.....{}
        ]
        ....... same for property , education, wedding, event
    }
    :param user_id: the id of user who logged in
    :return: the answers the user have answered earlier
    """
    user_tax_answers, user_retirement_answers, user_property_answers = [], [], []
    user_education_answers, user_wedding_answers, user_event_answers = [], [], []
    user_assess_answers, user_investment_answers, user_plan_answers = [], [], []
    user_liquid_answers,user_automobile_answers , user_vaction_answers , user_jewellery_answers = [], [],[],[]
    for answer in core_models.Answer.objects.filter(user_id=user_id).select_related('question'):
        #  filters the answers by the user and loops through each answer checking its category(question_for)
        #  according to the category append the answer in the respective list(user_tax_answers,user_event_answers, etc)
        if answer.question.question_for == constants.RETIREMENT:
            user_retirement_answers = append_list(answer, user_retirement_answers)
        elif answer.question.question_for == constants.TAX_SAVING:
            user_tax_answers = append_list(answer, user_tax_answers)
        elif answer.question.question_for == constants.BUY_PROPERTY:
            user_property_answers = append_list(answer, user_property_answers)
        elif answer.question.question_for == constants.EDUCATION:
            user_education_answers = append_list(answer, user_education_answers)
        elif answer.question.question_for == constants.WEDDING:
            user_wedding_answers = append_list(answer, user_wedding_answers)
        elif answer.question.question_for == constants.OTHER_EVENT:
            user_event_answers = append_list(answer, user_event_answers)
        elif answer.question.question_for == constants.ASSESS:
            user_assess_answers = append_list(answer, user_assess_answers)
        elif answer.question.question_for == constants.INVEST:
            user_investment_answers = append_list(answer, user_investment_answers)
        elif answer.question.question_for == constants.PLAN:
            user_plan_answers = append_list(answer, user_plan_answers)
        elif answer.question.question_for == constants.LIQUID_GOAL:
            user_liquid_answers = append_list(answer, user_liquid_answers)
        elif answer.question.question_for == constants.AUTO_MOBILE:
            user_automobile_answers = append_list(answer, user_automobile_answers)
        elif answer.question.question_for == constants.VACATION:
            user_vaction_answers = append_list(answer, user_vaction_answers)
        elif answer.question.question_for == constants.JEWELLERY:
            user_jewellery_answers = append_list(answer, user_jewellery_answers)
    #  make a dictionary with keys 'tax','retirement'....'event' and value as respective list.
    user_answers = {'tax': user_tax_answers, 'retirement': user_retirement_answers, 'property': user_property_answers,
                    'education': user_education_answers, 'wedding': user_wedding_answers, 'event': user_event_answers,
                    'assess': user_assess_answers, 'investment': user_investment_answers, 'plan': user_plan_answers,
                    'liquid':user_liquid_answers, 'automobile':user_automobile_answers,'vacation':user_vaction_answers,
                    'jewellery':user_jewellery_answers
                    }
    return user_answers


def append_list(answer, user_type_answers):
    """
    Appends the current answer to the user_type_answers list according to whether the question is radio, multi-text
    or text
    and returns the appended list
    :param answer: the current answer to be appended
    :param user_type_answers: the list to which the answer is to be appended into.
    :return: returns the appended list
    """
    if answer.question.type is constants.RADIO:
        # in case of radio we add option id in text
        user_type_answers.append(helpers.make_dictionary(
                answer.question.question_id,
                core_models.Option.objects.get(id=answer.option_id).option_id, answer.metadata))
    elif answer.question.type is constants.MULTIPLE_TEXT:
        for user_type_answer in user_type_answers:
            if user_type_answer['question_id'] == answer.question.question_id:
                # checks if an answer with same question id is already present in the list
                # if present append text and metadata of present answer in already present answer list
                user_type_answer['answer'].append({'text': answer.text, 'metadata': answer.metadata})
                return user_type_answers
        user_type_answers.append(helpers.make_dictionary(answer.question.question_id, answer.text, answer.metadata))
    elif answer.question.type is constants.TEXT:
        user_type_answers.append(helpers.make_dictionary(answer.question.question_id, answer.text, answer.metadata))
    return user_type_answers


def get_assets(user):
    """
    Returns asset allocation for a user for each category in form of a dictionary
    :param user: the user we need to return the asset allocation
    :return:asset allocation for a a user for diff categories
    """
    user_asset_allocation, created = core_models.PlanAssestAllocation.objects.get_or_create(user=user)
    asset_allocation = {'tax': user_asset_allocation.tax_allocation,
                        'retirement': user_asset_allocation.retirement_allocation,
                        'property': user_asset_allocation.property_allocation,
                        'education': user_asset_allocation.education_allocation,
                        'wedding': user_asset_allocation.wedding_allocation,
                        'event': user_asset_allocation.event_allocation,
                        'invest': user_asset_allocation.invest_allocation,
                        'liquid':user_asset_allocation.liquid_allocation,
                        'automobile':user_asset_allocation.automobile_allocation,
                        'vacation':user_asset_allocation.vacation_allocation,
                        'jewellery':user_asset_allocation.jewellery_allocation
                        }
    return asset_allocation


def get_sms_verification_code(user):
    """
    :param user:
    :return: sms code of a user by either creating it or getting it from db
    """
    object, created = profile_models.VerificationSMSCode.objects.get_or_create(user=user)
    if (datetime.now() - object.modified_at).total_seconds() > 900 or created:  # more than 15 minutes or if created
        sms_code = random_with_N_digits(5)
        object.sms_code = sms_code
        object.save()
    return object.sms_code


def generate_address(address_dict):
    """
    returns a dictionary containing the unique pincode object after extracting based on the combination
    of the pincode, city, and state.
    :param address_dict: contains the request dictionary.
    :return: boolean and address_dict: which is the address object with the correct pincode object.
    """
    if address_dict.get('pincode') is not None and address_dict.get('pincode') != "":
        try:
            pincode = profile_models.Pincode.objects.get(pincode=address_dict.get('pincode'), city=address_dict.get('city'),
                                                         state=address_dict.get('state'))
        except profile_models.Pincode.DoesNotExist:
            return False, {}
        address_dict['pincode'] = pincode.id
    else:
        return False, {}
    address_dict.pop('city')
    address_dict.pop('state')
    return True, address_dict


def get_cheque_image_nominee_signature_front_image(target_user):
    """
    :param target_user:the user whose image path has to be returned
    :return: the image path of user
    """
    try:
        cheque_image = profile_models.InvestorBankDetails.objects.get(user=target_user).bank_cheque_image
    except profile_models.InvestorBankDetails.DoesNotExist:
        cheque_image = ""
    try:
        nominee = profile_models.NomineeInfo.objects.get(user=target_user)
        if nominee.nominee_absent:
            nominee_signature = "/"
        else:
            nominee_signature = nominee.nominee_signature
    except profile_models.NomineeInfo.DoesNotExist:
        nominee_signature = ""
    try:
        contact_front_image = profile_models.ContactInfo.objects.get(user=target_user).front_image
    except profile_models.ContactInfo.DoesNotExist:
        contact_front_image = ""
    try:
        pan_image = profile_models.InvestorInfo.objects.get(user=target_user).pan_image
    except profile_models.InvestorInfo.DoesNotExist:
        pan_image = ""

    return [cheque_image, nominee_signature, contact_front_image, pan_image]


def get_vault_dict(target_user):
    """
    :param target_user:the user whose image path has to be returned
    :return: dict with image paths
    """
    try:
        cheque_image = profile_models.InvestorBankDetails.objects.get(user=target_user).bank_cheque_image
    except profile_models.InvestorBankDetails.DoesNotExist:
        cheque_image = ""
    try:
        nominee = profile_models.NomineeInfo.objects.get(user=target_user)
    except profile_models.NomineeInfo.DoesNotExist:
        nominee = ""
    # try:
    #     contact = profile_models.ContactInfo.objects.get(user=target_user)
    #
    #     if contact.address_are_equal:
    #         '''
    #         Both addresses are equal.
    #         '''
    #         contact_info = contact.front_image
    #     else:
    #         '''
    #         Both are different
    #         '''
    #         if contact.front_image != "" and contact.permanent_front_image != "":
    #             '''Both are present and are different'''
    #             contact_info = "/"
    #         else:
    #             '''
    #             if both the images are not present
    #             '''
    #             contact_info = ""
    # except profile_models.ContactInfo.DoesNotExist:
    #     contact_info = ""
    try:
        contact_info = profile_models.ContactInfo.objects.get(user=target_user).front_image
    except Exception as e:
        contact_info = ""
    try:
        pan_image = profile_models.InvestorInfo.objects.get(user=target_user).pan_image
    except profile_models.InvestorInfo.DoesNotExist:
        pan_image = ""

    vault_dict = {
            'is_bank_info': cheque_image,
            'is_nominee_info': nominee,
            'is_contact_info': contact_info,
            'is_investor_info': pan_image,
            'is_identity_info': target_user.identity_info_image
        }
    return vault_dict

def current_vault_status(user):
    """
    :param user:
    :return: Return vault status flags
    """
    flags = {
            'is_bank_info': 0,
            'is_nominee_info': 0,
            'is_contact_info': 0,
            'is_investor_info': 0,
            'is_identity_info': 0
        }
    vault_dict = get_vault_dict(user)
    for key, values in flags.items():
        if vault_dict[key] != "" and getattr(user, key) is True:
            flags[key] = 2
    if user.get_kra_verified() == True:
        flags["is_identity_info"] = 1 if vault_dict["is_identity_info"] == "" else flags["is_identity_info"]
        flags["is_contact_info"] = 2 if getattr(user, 'is_contact_info') is True else 0

    return flags

def is_investable(user):
    """
    This is used to see if all the 5 flag are within the allowed category to invest
    :param user: user that wants to confirm completion.
    :return: True if within the investable range
    """
    flags = current_vault_status(user)
    flag_list = [
        flags['is_bank_info'],
        flags['is_nominee_info'],
        flags['is_contact_info'],
        flags['is_investor_info'],
        flags['is_identity_info']
    ]
    if user.get_kra_verified() == False and flag_list == [2,2,2,2,2]:
        return True
    elif user.get_kra_verified() == True and flag_list in [[2,2,2,2,2],[2,2,2,2,1]]:
        return True
    else:
        return False


def check_existing_user(**kwargs):
    """
    utility to check if existing user is present with a given email id or phone number
    If a user exists with either email or phone and neither the email and phone number is verified then delete the
    existing user

    :param kwargs: contains email and phone number
    :return:
    """
    email = kwargs['email']
    phone = kwargs['phone_number']

    logger = logging.getLogger('django.debug')
    logger.debug("Profiles: check_existing_user")

    try:
        user1 = profile_models.User.objects.get(email=email)
    except profile_models.User.DoesNotExist:
        user1 = None

    try:
        user2 = profile_models.User.objects.get(phone_number=phone)
    except profile_models.User.DoesNotExist:
        user2 = None

    if user1 is None and user2 is None:
        return

    if user1 == user2:
        if not user1.email_verified and not user1.phone_number_verified:
            logger.debug("Profiles: check_existing_user: Deleting user: " + user1.id)
            user1.delete()
            return

    if user1 is None:
        if not user2.email_verified and not user2.phone_number_verified:
            logger.debug("Profiles: check_existing_user: Deleting user2: " + user2.id)
            user2.delete()
            return

    if user2 is None:
        if not user1.email_verified and not user1.phone_number_verified:
            logger.debug("Profiles: check_existing_user: Deleting user1: " + user1.id)
            user1.delete()
            return

    if user1 != user2 and user1 is not None:
            if not user1.email_verified and not user1.phone_number_verified and not user2.email_verified and not user2.phone_number_verified:
                logger.debug("Profiles: check_existing_user: Deleting users: " + user1.id + " " + user2.id)
                user1.delete()
                user2.delete()
                return


def get_situation(**kwargs):
    """
    This method takes email, phone_number and password to handle various cases of Registering User.

    The various cases are:
    000 - both email and phone are same as previously registered values + same password is used + verified: please
    login.
    001 - both same + same password + not verified(either phone or email is not verified) : Please verify first.
    010 - both same + different password + verified: user already exists please login.
    011 - both different(both email and phone are different than the previously registered one.): new user creation.
    100 - only email matches: user with this email already exists
    101 - only phone matches: user with this phone_number already exists
    110 - both same + different password + not verified: update user's password and ask them to verify.
    111 - <open for future use>
    :param kwargs: contains the email and phone number
    :return: the case number of the registration situation.
    """

    email = kwargs['email']
    phone = kwargs['phone_number']
    password = kwargs['password']
    kwargs.pop('password')
    flags = ['0'] * 3  # bit-set emulation to represent the 7 cases.

    #  lookup dictionary to return from.
    cases = {'000': cons.SIGNUP_ERROR_0, '001': cons.SIGNUP_ERROR_1, '010': cons.SIGNUP_ERROR_2,
             '011': cons.SIGNUP_ERROR_3, '100': cons.SIGNUP_ERROR_4, '101': cons.SIGNUP_ERROR_5,
             '110': cons.SIGNUP_ERROR_6}
    try:
        user = profile_models.User.objects.get(email__iexact=email, phone_number=phone)
    except profile_models.User.DoesNotExist:
        # user doesn't exist with unique combination of email and phone number
        try:
            # check if user with that email only exists. case 4
            user = profile_models.User.objects.get(email__iexact=email)
            flags = ['1', '0', '0']
        except profile_models.User.DoesNotExist:
            # user with that email does not exist.So check if user with that phone only exists.
            # case 5
            try:
                user = profile_models.User.objects.get(phone_number=phone)
                flags = ['1', '0', '1']
            except profile_models.User.DoesNotExist:
                # totally new user. Have to create this guy. case 3
                user = None
                flags = ['0', '1', '1']

    if user and not user.check_password(password) and flags == ['0', '0', '0']:
        # password is a new password.

        if not user.email_verified and not user.phone_number_verified:
            # not verified case 6.
            flags = ['1', '1', '0']
        else:
            # both verified. case 2
            flags = ['0', '1', '0']

    # else password is same.
    elif user and flags == ['0', '0', '0']:
        # if any one is not verified. case 1
        if not user.email_verified and not user.phone_number_verified:
            flags = ['0', '0', '1']
        else:
            # both verified. case 0
            flags = ['0']*3

    return cases[''.join(flags)]


def set_user_check_attributes(user, attribute):
    """
    :param user:user whose attribute is to be set
    :param attribute:the attribute which needs to be set to True
    :return:
    """
    setattr(user, attribute, True)
    user.save()


def send_daily_mails_for_bse_registration():
    """
    Sends daily mail for bse registration
    :return:
    """
    investor_list = profile_models.InvestorInfo.objects.filter(kra_verified=True, user__bse_registered=False)
    final_list = []
    for investor in investor_list:
        if is_investable(investor.user) is True:
            final_list.append(investor.user.email)
    if len(final_list) != 0:
        helpers.send_bse_registration_email(final_list, use_https=settings.USE_HTTPS)


def send_daily_mails_for_kyc_verification():
    """
    Send daily mail for kyc verification
    :return:
    """
    investor_list = profile_models.InvestorInfo.objects.filter(kra_verified=False, user__bse_registered=False)
    final_list = []
    for investor in investor_list:
        if is_investable(investor.user) is True and investor.user.signature != "":
            final_list.append(investor.user.email)
    if len(final_list) != 0:
        helpers.send_kyc_verification_email(final_list, use_https=settings.USE_HTTPS)

def update_kyc_status():
    """
    Update kyc verification status by checking with cvl
    :return:
    """

    logger = logging.getLogger('django.debug')
    logger.debug("Profiles: update_kyc_status")

    investor_list = profile_models.InvestorInfo.objects.filter(kra_verified=False, pan_number__isnull=False)
    for investor in investor_list:
        password = cvl.get_cvl_password()
        pan_status, name = cvl.get_pancard_status(password, investor.pan_number)
        new_status = True if pan_status[-2:] in ["02", "002"] else False
        if new_status is True:
            logger.debug("Profiles: update_kyc_status: KYC Verified for user id: " + investor.user.id)
            investor.kra_verified = True
            investor.save()

def get_order_sip_amount(user, order_detail):
    sip_amount = 0;
    if order_detail is not None:
        if order_detail.order_status != core_models.OrderDetail.OrderStatus.Cancelled:
            sip_amount = order_detail.fund_order_items.aggregate(total=Sum(F('agreed_sip')))['total']
    return sip_amount

def get_mandate_total_sip_amount(user, mandate):
        sip_amount = 0;
        try:
            if mandate:
                order_details = core_models.OrderDetail.objects.filter(user=user, is_lumpsum=True, bank_mandate=mandate).exclude(order_status=core_models.OrderDetail.OrderStatus.Cancelled)
                for o in order_details:
                    sip_amount += o.fund_order_items.aggregate(total=Sum(F('agreed_sip')))['total']
                
        except core_models.OrderDetail.DoesNotExist:
            pass
        return sip_amount


def check_existing_user_email(**kwargs):
    email = kwargs['email']

    logger = logging.getLogger('django.debug')
    logger.debug("Profiles: check_existing_user_email")

    try:
        ## Check the user in the profile user table
        user = profile_models.User.objects.get(email__iexact=email)
        try:
            ## If user in profile user table , check user in social auth user table
            social_user = social_model.UserSocialAuth.objects.filter(user=user).exists()
           
            ## returns True if exist else Flase
            if social_user == True:
                result =  cons.GOOGLE_LOGIN_EXIST_GOOGLE_USER
            else:
                result = cons.GOOGLE_LOGIN_EXIST_FINASKUS_USER
        except:
            result =  cons.GOOGLE_LOGIN_EXIST_FINASKUS_USER
    except profile_models.User.DoesNotExist:
        result = cons.GOOGLE_REGISTER
        user = None
        
    return user,result


def get_social_user(email):
    try:
        user = profile_models.User.objects.get(email__iexact=email)
    except profile_models.User.DoesNotExist:
        user = None
    return user

def phone_number_check(phone):
    try:
        user = profile_models.User.objects.get(phone_number=phone)
    except profile_models.User.DoesNotExist:
        user = None
    return user


def create_thumbnail(img,thumbnail):
    """
    It creates thumbnail for the uploaded images
    param: image - original uploaded image field
           thumbnail - thumbnail field for the images
    """
    
    if img != "" and img is not None:
        THUMB_SIZE = (100,100)

        try:
            image = Image.open(img)
        except:
            return False
 
        image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        
        # Path to save to, name, and extension
        thumb_name, thumb_extension = os.path.splitext(img.name)
        thumb_extension = thumb_extension.lower()
        
        if thumb_extension.endswith('"'):
            thumb_extension = thumb_extension[:-1]
        
        thumb_filename = thumb_name + thumb_extension
    
        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type
    
        # Save thumbnail to in-memory file as StringIO
        temp_thumb = io.BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)
            # Load a ContentFile into the thumbnail field so it gets saved
        try:
            thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        except:
            temp_thumb.close()
            return False
        temp_thumb.close()
        return True
    else:
        return False

