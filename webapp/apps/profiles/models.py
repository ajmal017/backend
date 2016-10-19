# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djutil.models import TimeStampedModel
from dateutil.relativedelta import relativedelta


from api import utils as api_utils
from external_api.models import Pincode, BankDetails
from . import manager, constants, helpers

from enum import Enum
from enum import IntEnum
from datetime import date
import os

def unique_identity_image(instance, filename):
    return "user/" + instance.id + "/identity/image/" + filename

def unique_identity_image_thumbnail(instance, filename):
    return "user/" + instance.id + "/identity/image/thumbnail" + filename

def unique_profile_image(instance, filename):
    return "user/" + instance.id + "/profile/image/" + filename

def unique_profile_image_thumbnail(instance, filename):
    return "user/" + instance.id + "/profile/image/thumbnail" + filename

def unique_signature_image(instance, filename):
    return "user/" + instance.id + "/signature/image/" + filename

def unique_kyc_video(instance, filename):
    return "user/" + instance.id + "/kyc/video/" + filename    

def unique_kycvideo_image(instance, filename):
    return "user/" + instance.id + "/kycvideo/image/" + filename    

def unique_pan_image(instance, filename):
    return "user/" + instance.user.id + "/pan/image/" + filename

def unique_pan_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/pan/image/thumbnail" + filename

def unique_permanentaddress_front_image(instance, filename):
    return "user/" + instance.user.id + "/permanentaddressfront/image/" + filename

def unique_permanentaddress_front_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/permanentaddressfront/image/thumbnail" + filename
    
def unique_permanentaddress_back_image(instance, filename):
    return "user/" + instance.user.id + "/permanentaddressback/image/" + filename

def unique_permanentaddress_back_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/permanentaddressback/image/thumbnail" + filename

def unique_addressfront_image(instance, filename):
    return "user/" + instance.user.id + "/addressfront/image/" + filename

def unique_addressfront_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/addressfront/image/thumbnail" + filename

def unique_addressback_image(instance, filename):
    return "user/" + instance.user.id + "/addressback/image/" + filename

def unique_addressback_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/addressback/image/thumbnail" + filename

def unique_nomineesignature_image(instance, filename):
    return "user/" + instance.user.id + "/nomineesignature/image/" + filename

def unique_cheque_image(instance, filename):
    return "user/" + instance.user.id + "/cheque/image/" + filename

def unique_cheque_image_thumbnail(instance, filename):
    return "user/" + instance.user.id + "/cheque/image/thumbnail" + filename
    
class S3PrivateFileField(models.FileField):

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(S3PrivateFileField, self).__init__(verbose_name=verbose_name,
                name=name, upload_to=upload_to, storage=storage, **kwargs)
        self.storage.default_acl = "private"

class S3PrivateImageField(models.ImageField):

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(S3PrivateImageField, self).__init__(verbose_name=verbose_name,
                name=name, upload_to=upload_to, storage=storage, **kwargs)
        self.storage.default_acl = "private"

class User(AbstractBaseUser, TimeStampedModel):
    """

    """
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    MARITAL_STATUS_CHOICES = (
        (constants.LEVEL_1, 'Single'),
        (constants.LEVEL_2, 'Married')
    )
    PROCESS_CHOICES = (
        (constants.LEVEL_0, 'Completely paperless online process'),
        (constants.LEVEL_1, 'Print and courier yourself'),
        (constants.LEVEL_2, 'Doorstep representative'),
    )
    MANDATE_STATUS = (
        (constants.LEVEL_0, 'Pending'),
        (constants.LEVEL_1, 'Ongoing'),
        (constants.LEVEL_2, 'Completed'),
    )

    id = models.CharField(_('user id'), max_length=20, primary_key=True)
    first_name = models.CharField(_('first name'), max_length=254, blank=True, default="")
    middle_name = models.CharField(_('middle name'), max_length=254, blank=True, default="")
    last_name = models.CharField(_('last name'), max_length=254, blank=True, default="")
    username = models.CharField(_('username'), max_length=254, unique=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    phone_regex = RegexValidator(regex='[0-9]{10,12}',
                                 message=_("Phone number must be entered in the format:"
                                            " '9999999999'. Up to 12 digits allowed."))
    phone_number = models.CharField(_('phone_number'), validators=[phone_regex], max_length=12, blank=False, null=False, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default="")
    dob = models.DateField(_('dob'), blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=False,
    help_text=_('Designates whether this user should be treated as active. Unselect it instead of deleting accounts.'))
    vault_locked = models.BooleanField(help_text=_('Is vault locked?'), default=False)
    if settings.USING_S3 is True:
        image = S3PrivateImageField(upload_to=unique_profile_image, max_length=700, blank=True, null=True)
        image_thumbanil = S3PrivateImageField(upload_to=unique_profile_image_thumbnail, max_length=700, blank=True, null=True)
    else:
        image = models.ImageField(upload_to="profile/image/", max_length=700, blank=True, null=True)
        image_thumbnail = models.ImageField(upload_to="profile/image/thumbnail", max_length=700, blank=True, null=True)
    country_of_birth = models.CharField(_('country of birth'), max_length=254, blank=True, default="")
    nationality = models.CharField(_('nationality'), max_length=254, blank=True, default="")
    tax_status = models.CharField(_('tax status'), max_length=254, blank=True, default="",
    help_text=_('Check whether user is tax payer in other country.'))
    risk_score = models.FloatField(null=True, blank=True)
    phone_number_verified = models.BooleanField(_('phone number verification status'), default=False)
    email_verified = models.BooleanField(_('email verification status'), default=False)
    age = models.IntegerField(_('age'), blank=True, null=True)
    if settings.USING_S3 is True:
        identity_info_image = S3PrivateImageField(upload_to=unique_identity_image, max_length=700, blank=True, null=True)
        identity_info_image_thumbnail = S3PrivateImageField(upload_to=unique_identity_image_thumbnail, max_length=700, blank=True, null=True)
    else:
        identity_info_image = models.FileField(upload_to="identity/image/", max_length=700, blank=True, null=True)
        identity_info_image_thumbnail = models.FileField(upload_to="identity/image/thumbnail", max_length=700, blank=True, null=True)
    marital_status = models.CharField(choices=MARITAL_STATUS_CHOICES, max_length=1, default="")
    is_investor_info = models.BooleanField(_('is investor info complete'), default=False)
    is_contact_info = models.BooleanField(_('is contact info complete'), default=False)
    is_identity_info = models.BooleanField(_('is identity info complete'), default=False)
    is_bank_info = models.BooleanField(_('is bank info complete'), default=False)
    is_nominee_info = models.BooleanField(_('is nominee info complete'), default=False)
    is_declaration = models.BooleanField(_('is declaration complete'), default=False)
    is_terms = models.BooleanField(_('is terms and conditions accepted'), default=False)
    process_choice = models.CharField(max_length=1, choices=PROCESS_CHOICES, blank=True, default="")
    mandate_status = models.CharField(max_length=1, choices=MANDATE_STATUS, blank=True, default=constants.LEVEL_0)
    xsip_status = models.CharField(max_length=1, choices=MANDATE_STATUS, blank=True, default=constants.LEVEL_0)
    if settings.USING_S3 is True:
        signature = S3PrivateImageField(upload_to=unique_signature_image, max_length=700, blank=True, null=True)
    else:
        signature = models.FileField(upload_to="user/signature/", max_length=700, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    finaskus_id = models.CharField(max_length=40, default=None, blank=True, null=True)
    mandate_reg_no = models.CharField(_('Mandate Registration Number'), max_length=100, default=None, blank=True,
                                      null=True)
    bse_registered = models.BooleanField(default=False)
    fatca_filed = models.BooleanField(default=False)
    tiff_mailed = models.BooleanField(default=False)
    tiff_accepted = models.BooleanField(default=False)
    kyc_mailed = models.BooleanField(default=False)
    kyc_accepted = models.BooleanField(default=False)
    is_virtual_seen = models.BooleanField(default=False)
    is_real_seen = models.BooleanField(default=False)
    rebuild_portfolio = models.BooleanField(default=False)
    if settings.USING_S3 is True:
        user_video = S3PrivateFileField(upload_to=unique_kyc_video, max_length=700, blank=True, null=True)
    else:
        user_video = models.FileField(upload_to="user_video/", max_length=700, blank=True, null=True)
    if settings.USING_S3 is True:
        user_video_thumbnail = S3PrivateImageField(upload_to=unique_kycvideo_image, max_length=700, blank=True, null=True)
    else:
        user_video_thumbnail = models.FileField(upload_to="user_video/thumbnail/", max_length=700, blank=True, null=True)
        
    USERNAME_FIELD = 'email'

    objects = manager.CustomUserManager()

    # class Meta:
    #     """
    #
    #     """
    #     app_label = 'profiles'

    def __str__(self):
        return str(self.email)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.user_video:
                orig = User.objects.get(pk=self.pk)
                if not orig.user_video:
                    helpers.send_user_video_upload_email(self,use_https=settings.USE_HTTPS)
            if self.image:
                orig = User.objects.get(pk=self.pk)
                if self.image != orig.image:
                    print(os.path.abspath(self.image.url))
                    
                   
        if not self.id:
            self.id = api_utils.gen_hash(api_utils.expires())
        if self.vault_locked==False:
            self.is_terms = False
            self.is_declaration = False
        
        

        self.clean()

        super(User, self).save(*args, **kwargs)

    def clean(self):
        super(User, self).clean()
        if self.email:
            self.username = self.email 
    
    @property
    def is_superuser(self):
        return self.is_staff

    @property
    def is_admin(self):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(x for x in parts if x)

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name.strip()

    def get_kra_verified(self):
        """
        To show kra verification on user admin
        """
        try:
            return self.investorinfo.kra_verified
        except Exception:
            return False

    def get_sip_tenure(self, portfolio):
        """
        Returns SIP tenure
        :params portfolio: portfolio for which sip tenure needs to be calculated
        """
        texts = []
        answers = self.user.filter(question__question_id='term', portfolio=portfolio)
        difference_in_age = api_utils.age_calculator(self.user, portfolio)
        texts = [int(answer.text) for answer in answers]
        if difference_in_age is not None:
            texts.append(difference_in_age)
        texts = list(filter(lambda key: key != 0, texts))
        if len(texts) == 0:
            return None
        return min(texts),len(texts)
    

class VerificationSMSCode(TimeStampedModel):
    """
    Stores a short 5 digit activation code for verification
    """
    user = models.OneToOneField(User)
    sms_code = models.IntegerField(default=00000)

    def __str__(self):
        return str(self.user.email) + " " + str(self.user.phone_number)


class EmailCode(TimeStampedModel):
    """
    Stores an alphanumeric code of length 50 for verification
    """
    user = models.OneToOneField(User)
    code = models.CharField(max_length=50)
    expires_at = models.DateTimeField(auto_now=False)

    def __str__(self):
        return str(self.user.email) + " " + str(self.user.phone_number)


class InvestorInfo(TimeStampedModel):
    """

    """
    OCCUPATION_TYPE_CHOICE = (
        (constants.PRIVATE_SECTOR, 'Private Sector Service'),
        (constants.PROFESSIONAL, 'Professional (Self-Employed)'),
        (constants.BUSINESS, 'Business'),
        (constants.HOUSEWIFE, 'Housewife'),
        (constants.PUBLIC_SECTOR, 'Public Sector Service'),
        (constants.GOVERNMENT, 'Government Service'),
        (constants.RETIRED, 'Retired'),
        (constants.FOREX_DEALER, 'Forex Dealer'),
        (constants.AGRICULTURE, 'Agriculturist'),
        (constants.STUDENT, 'Student'),
        (constants.OTHER, 'Other (please specify)')
    )
    INCOME_CHOICE = (
        (constants.LEVEL_1, '< 1 Lakh'),
        (constants.LEVEL_2, '1-5 Lakhs'),
        (constants.LEVEL_3, '5-10 Lakhs'),
        (constants.LEVEL_4, '10-25 Lakhs'),
        (constants.LEVEL_5, '25-100 Lakhs'),
        (constants.LEVEL_6, '> 100 Lakhs')
    )
    EXPOSURE_CHOICE = (
        (constants.LEVEL_1 , 'Not applicable'),
        (constants.LEVEL_2 , 'I am a PEP'),
        (constants.LEVEL_3 , 'I am related to PEP')
    )
    pan_validator = RegexValidator(regex='^([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}',
                                 message=_("Pan number must be entered in the format:'AAAPL1234C'"))

    user = models.OneToOneField(User)
    investor_status = models.CharField(max_length=100, default="Resident Individual")
    pan_number = models.CharField(_('Pan Number'), validators=[pan_validator], max_length=12, blank=True,
                                  null=True, unique=True)
    applicant_name = models.CharField(max_length=512, blank=True, null=True)
    father_name = models.CharField(max_length=512, blank=True, null=True)
    dob = models.DateField(_('dob'), blank=True, null=True)
    country_of_birth = models.CharField(_('country of birth'), max_length=254, blank=True, null=True)
    place_of_birth = models.CharField(_('place of birth'), max_length=254, blank=True, null=True)

    income = models.CharField(max_length=1, choices=INCOME_CHOICE, blank=True, null=True)
    political_exposure = models.CharField(max_length=1, choices=EXPOSURE_CHOICE, blank=True, null=True)
    occupation_type = models.CharField(max_length=3, blank=True, null=True, default=None,
                                       choices=OCCUPATION_TYPE_CHOICE)
    occupation_specific = models.CharField(max_length=512, blank=True, null=True)
    other_tax_payer = models.BooleanField(default=False,help_text=_(u'Do you pay tax in country other than India'))
    if settings.USING_S3 is True:
        pan_image = S3PrivateImageField(upload_to=unique_pan_image, max_length=700, blank=True, null=True)
        pan_image_thumbnail = S3PrivateImageField(upload_to=unique_pan_image_thumbnail, max_length=700, blank=True, null=True)
    else:
        pan_image = models.FileField(upload_to="investor_info/pan/image", max_length=700, blank=True, null=True)
        pan_image_thumbnail = models.FileField(upload_to="investor_info/pan/image/thumbnail", max_length=700, blank=True, null=True)
    kra_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user) + " " + str(self.pan_number)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.kra_verified is True:
                orig = InvestorInfo.objects.get(pk=self.pk)
                if orig.kra_verified is False:
                    helpers.send_kra_verified_email(orig.user, self.applicant_name, use_https=settings.USE_HTTPS)
        super(InvestorInfo, self).save(*args, **kwargs)

    def get_dob(self):
        if self.dob:
            return self.dob
        else:
            return None

class Address(models.Model):
    """
    """
    pincode = models.ForeignKey(Pincode)
    address_line_1 = models.CharField(max_length=2048, blank=True, null=True)
    address_line_2 = models.CharField(max_length=2048, blank=True, null=True)
    nearest_landmark = models.CharField(max_length=2048, blank=True, null=True)

    def __str__(self):
        return str(self.address_line_1)


class ContactInfo(TimeStampedModel):
    """

    """

    class AddressProofs(IntEnum):
        """
        this is used for the choices of the address_proof_type.
        """
        Passport = 1
        Driving_License = 2
        Voter_ID_Card = 3
        Aadhaar_Card = 4
        Bank_Statement = 5
        Utility_Bill = 6
        Ration_Card = 7
        Lease = 8

    class AddressType(IntEnum):
        Residential = 1
        Business = 2
        Residential_Business = 3
        Registered_Office = 4
        
    user = models.OneToOneField(User)
    communication_address = models.ForeignKey(Address, related_name="user_communication_address", blank=True, null=True)
    communication_address_type = models.IntegerField(choices=[(x.value, x.name) for x in AddressType], default=None,
                                             null=True)
    permanent_address = models.ForeignKey(Address, related_name="user_permanent_address", blank=True, null=True)
    address_are_equal = models.BooleanField(default=False, help_text=_(u'Is communication and permanent address same'))
    address_proof_type = models.IntegerField(choices=[(x.value, x.name) for x in AddressProofs], default=None,
                                             null=True)
    permanent_address_proof_type = models.IntegerField(choices=[(x.value, x.name) for x in AddressProofs], default=None,
                                                       null=True)
    email = models.EmailField(_('email address'), max_length=254, blank=True, null=True)
    phone_number = models.CharField(_('phone_number'), max_length=12, blank=True, null=True)
    if settings.USING_S3 is True:
        # front image of the address proof.
        front_image = S3PrivateImageField(upload_to=unique_addressfront_image, max_length=1023, blank=True, null=True)
        front_image_thumbnail = S3PrivateImageField(upload_to=unique_addressfront_image_thumbnail, max_length=1023, blank=True, null=True)
        # back image of the address proof.
        back_image = S3PrivateImageField(upload_to=unique_addressback_image, max_length=1023, blank=True, null=True)
        back_image_thumbnail = S3PrivateImageField(upload_to=unique_addressback_image_thumbnail, max_length=1023, blank=True, null=True)
        # front image of the permanent address proof.
        permanent_front_image = S3PrivateImageField(upload_to=unique_permanentaddress_front_image, max_length=1023, blank=True, null=True)
        permanent_front_image_thumbnail = S3PrivateImageField(upload_to=unique_permanentaddress_front_image_thumbnail, max_length=1023, blank=True, null=True)
        # back image of the permanent address proof.
        permanent_back_image = S3PrivateImageField(upload_to=unique_permanentaddress_front_image, max_length=1023, blank=True, null=True)
        permanent_back_image_thumbnail = S3PrivateImageField(upload_to=unique_permanentaddress_front_image_thumbnail, max_length=1023, blank=True, null=True)
    else:
        # front image of the address proof.
        front_image = models.FileField(upload_to="contact/address_proof/", max_length=1023, blank=True, null=True)
        front_image_thumbnail = models.FileField(upload_to="contact/address_proof/thumbnail", max_length=1023, blank=True, null=True)
        # back image of the address proof.
        back_image = models.FileField(upload_to="contact/address_proof/", max_length=1023, blank=True, null=True)
        back_image_thumbnail = models.FileField(upload_to="contact/address_proof/thumbnail", max_length=1023, blank=True, null=True)
        # front image of the permanent address proof.
        permanent_front_image = models.FileField(upload_to="contact/permanent_address_proof/", max_length=1023, blank=True, null=True)
        permanent_front_image_thumbnail = models.FileField(upload_to="contact/permanent_address_proof/thumbnail", max_length=1023, blank=True, null=True)
        # back image of the permanent address proof.
        permanent_back_image = models.FileField(upload_to="contact/permanent_address_proof/", max_length=1023, blank=True, null=True)
        permanent_back_image_thumbnail = models.FileField(upload_to="contact/permanent_address_proof/thumbnail", max_length=1023, blank=True, null=True)

    def __str__(self):
        return str(self.user) + " " + str(self.communication_address)


class InvestorBankDetails(TimeStampedModel):
    """
    Model to save investor bank details
    """
    class AccountType(Enum):
        Savings = 'S'
        Current = 'C'

    ifsc_code = models.ForeignKey(BankDetails, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=1, choices=[(x.value, x.name.title()) for x in AccountType])
    sip_check = models.BooleanField(default=False)
    if settings.USING_S3 is True:
        bank_cheque_image = S3PrivateImageField(upload_to=unique_cheque_image, max_length=1023, blank=True, null=True)
        bank_cheque_image_thumbnail = S3PrivateImageField(upload_to=unique_cheque_image_thumbnail, max_length=1023, blank=True, null=True)
    else:
        bank_cheque_image = models.FileField(upload_to="cheque/image/", max_length=1023, blank=True, null=True)
        bank_cheque_image_thumbnail = models.FileField(upload_to="cheque/image/thumbnail", max_length=1023, blank=True, null=True)
    def __str__(self):
        return str(self.user) + " " + str(self.ifsc_code) + " " + str(self.account_holder_name)


class NomineeInfo(models.Model):
    """
    Details of the nominee.
    """
    class Relationship(IntEnum):
        """
        this is used for the choices of relationship_with_investor field.
        """
        Spouse = 1
        Parent = 2
        Offspring = 3
        Sibling = 4
        Other = 5

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    nominee_name = models.CharField(_('nominee name'), max_length=254, blank=True, default=None, null=True)
    nominee_dob = models.DateField(_('dob'), blank=True, null=True)
    guardian_name = models.CharField(_('guardian name'), max_length=254, blank=True, default=None, null=True)
    relationship_with_investor = models.IntegerField(choices=[(x.value, x.name) for x in Relationship], default=None,
                                                     null=True)
    nominee_address = models.ForeignKey(Address, related_name='nominee_address', default=None, null=True)
    nominee_absent = models.BooleanField(_('is nominee is absent'), default=False)
    address_are_equal = models.BooleanField(default=False, help_text=_(u'Is nominee address same as investor '
                                                                       u'communication address'))
    
    if settings.USING_S3 is True:
        nominee_signature = S3PrivateImageField(upload_to=unique_nomineesignature_image, max_length=700, blank=True, null=True)
    else:
        nominee_signature = models.FileField(upload_to="nominee/signature/", max_length=700, blank=True, null=True)
    def __str__(self):
        return str(self.user) + " " + str(self.nominee_name)


class AppointmentDetails(models.Model):
    """
    Appointment schedule meeting.
    """
    class Status(IntEnum):
        """
        this is used for the choices of appointment status for status field.
        """
        Pending = 0
        Ongoing = 1
        Complete = 2

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    address = models.ForeignKey(Address, related_name='appointment_address', default=None, null=True)
    date = models.DateField(_('appointment_date'), blank=True, null=True)
    time = models.TimeField(_('appointment_time'), blank=True, null=True)
    status = models.IntegerField(choices=[(x.value, x.name) for x in Status], default=Status.Pending.value)

    def __str__(self):
        return str(self.user) + " " + str(self.date) + " " + str(self.time)


class AggregatePortfolio(TimeStampedModel):
    """
    Stores total xirr of users used for leader board
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    total_xirr = models.FloatField(default=0.0, null=True, blank=True)
    update_date = models.DateField(blank=False, null=False)

    def get_rank(self):
        """
        :return: global ranking for the Leader Board.
        """

        return AggregatePortfolio.objects.filter(total_xirr__gt=self.total_xirr).count() + 1

    def __str__(self):
        return str(self.user.email) + " " + str(self.total_xirr) + " " + str(self.update_date)


    class Meta:
        ordering = ['-total_xirr']


class UserChangedPhoneNumber(TimeStampedModel):
    """
    Stores information of users who want to change their phone number
    """
    user = models.OneToOneField(User)
    sms_code = models.IntegerField(default=00000)
    phone_regex = RegexValidator(regex='[0-9]{10,12}',
                                 message=_("Phone number must be entered in the format:"
                                            " '9999999999'. Up to 12 digits allowed."))
    phone_number = models.CharField(_('phone_number'), validators=[phone_regex], max_length=12, blank=False, null=False, unique=True)

    def __str__(self):
        return str(self.user.email) + " " + str(self.user.phone_number)
