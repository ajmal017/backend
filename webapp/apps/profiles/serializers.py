from rest_framework import serializers
from rest_framework.validators import UniqueValidator


from . import models
from external_api.models import Pincode, BankDetails
from external_api import serializers as external_api_serializers


class UserSerializer(serializers.ModelSerializer):
    """
    User information Get and put API
    """
    name = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = models.User
        fields = ('email', 'phone_number', 'gender', 'name', 'first_name', 'last_name', 'image')


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User Information after login and signup
    """
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(read_only=True, source="get_full_name")

    class Meta:
        model = models.User
        fields = ('email', 'phone_number', 'password', 'risk_score', 'name', 'email_verified', 'phone_number_verified')


class SaveIdentityImageSerializer(serializers.ModelSerializer):
    """
    Identity info image saver serializer.
    """
    class Meta:
        model = models.User
        fields = ('identity_info_image',)


class EmailStatusSerializer(serializers.ModelSerializer):
    """
    User information Get and put API
    """

    class Meta:
        model = models.User
        fields = ('email', 'email_verified')


class InvestorInfoSerializer(serializers.ModelSerializer):
    """
    Investor Information Serializer used to store or display or update investor details
    """

    class Meta:
        model = models.InvestorInfo
        exclude = ('created_at', 'modified_at', 'user', 'kra_verified')

class InvestorInfoDateSerializer(serializers.ModelSerializer):
    """
    Investor Information Serializer used to store or display or update investor details
    """
    dob = serializers.DateField(source="get_dob", allow_null=True, required=False)

    class Meta:
        model = models.InvestorInfo
        exclude = ('created_at', 'modified_at', 'user', 'kra_verified')


class PincodeSerializer(serializers.ModelSerializer):
    """
    Pincode model serializer used to display pincode details
    """

    class Meta:
        model = Pincode
        fields = ('pincode', 'city', 'state')


class SavePanImageSerializer(serializers.ModelSerializer):
    """
    Serializer for saving the pan card image of the investor.
    """

    class Meta:
        model = models.InvestorInfo
        fields = ('pan_image',)


class SaveSignatureSerializer(serializers.ModelSerializer):
    """
    Serializer for saving the signature of the user.
    """

    class Meta:
        model = models.User
        fields = ('signature',)


class SaveNomineeSignatureSerializer(serializers.ModelSerializer):
    """
    Serializer for saving the signature of the nominee.
    """

    class Meta:
        model = models.NomineeInfo
        fields = ('nominee_signature',)


class BankChequeSerializer(serializers.ModelSerializer):
    """
    Serializer for saving bank_cheque_image
    """

    class Meta:
        model = models.InvestorBankDetails
        fields = ('bank_cheque_image',)


class AddressSerializer(serializers.ModelSerializer):
    """
    This is address serializer.
    This is for the continue button.    
    """
    pincode = serializers.PrimaryKeyRelatedField(queryset=Pincode.objects.all())
    address_line_1 = serializers.CharField(allow_blank=False, allow_null=False, max_length=2048, required=True)
    address_line_2 = serializers.CharField(allow_blank=True, allow_null=True, max_length=2048, required=False)
    nearest_landmark = serializers.CharField(allow_blank=True, allow_null=True, max_length=2048, required=False)

    class Meta:
        model = models.Address


class AddressSkipSerializer(serializers.ModelSerializer):
    """
    Serializer for Address objects.
    This is for the skip button.
    """

    class Meta:
        """

        """
        model = models.Address
        fields = ('pincode', 'address_line_1', 'address_line_2', 'nearest_landmark')


class ContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactInfo
    """
    communication_address = AddressSerializer()
    permanent_address = AddressSerializer()

    class Meta:
        """

        """
        model = models.ContactInfo
        fields = ('communication_address', 'permanent_address', 'address_are_equal', 'address_proof_type',
                  'front_image', 'back_image', 'email', 'phone_number')

    def create(self, validated_data):
        """
        this is used to handle the save call in order to manually handle the child serializers.
        :param validated_data: contains the dictionary of data which also includes serializers for communication and
        permanent addresses id fields.

        :return: the newly created contact object.
        """

        contact = models.ContactInfo.objects.create(**validated_data)
        return contact


class InvestorInfoRequiredSerializer(serializers.ModelSerializer):
    """

    """
    unique_validator = UniqueValidator(queryset=models.InvestorInfo.objects.all(), message="Pan card must be unique")
    father_name = serializers.CharField(max_length=512)
    applicant_name = serializers.CharField(max_length=512)
    id = serializers.IntegerField(label='ID', read_only=True)
    other_tax_payer = serializers.BooleanField(required=False)
    occupation_specific = serializers.CharField(max_length=512)
    dob = serializers.DateField(allow_null=True, required=False)
    pan_image = serializers.FileField(allow_null=True, required=False)
    investor_status = serializers.CharField(max_length=100, required=False)
    pan_number = serializers.CharField(label='Pan Number', max_length=12,
                                       validators=[models.InvestorInfo.pan_validator, unique_validator])
    income = serializers.ChoiceField(allow_null=True, choices=models.InvestorInfo.INCOME_CHOICE, required=False)
    political_exposure = serializers.ChoiceField(allow_null=True,
                                                 choices=models.InvestorInfo.EXPOSURE_CHOICE, required=False)
    occupation_type = serializers.ChoiceField(allow_null=True,
                                              choices=models.InvestorInfo.OCCUPATION_TYPE_CHOICE, required=False)

    class Meta:
        model = models.InvestorInfo
        exclude = ('created_at', 'modified_at', 'user', 'kra_verified')


class IdentityInfoGetSerializer(serializers.ModelSerializer):
    """
    User Information Serializer with only marital status, gender and nationality
    """

    class Meta:
        model = models.User
        fields = ('marital_status', 'gender', 'nationality', 'identity_info_image')


class IdentityInfoSkipSerializer(serializers.ModelSerializer):
    """
    User Information Serializer with only marital status, gender and nationality
    Post serializer for skip button
    """

    class Meta:
        model = models.User
        fields = ('marital_status', 'gender', 'nationality')


class IdentityInfoSerializer(serializers.ModelSerializer):
    """
    User Information Serializer with only marital status, gender and nationality
    Post serializer for continue button
    """
    marital_status = serializers.ChoiceField(choices=(('1', 'Single'), ('2', 'Married')), required=True)
    gender = serializers.ChoiceField(allow_blank=True, choices=(('M', 'Male'), ('F', 'Female')), required=True)
    nationality = serializers.CharField(allow_blank=True, max_length=254, required=True)

    class Meta:
        model = models.User
        fields = ('marital_status', 'gender', 'nationality')

class IdentityInfoOptionalSerializer(serializers.ModelSerializer):
    """
    User Information Serializer with only marital status, gender and nationality
    Post serializer for continue button
    """
    marital_status = serializers.ChoiceField(choices=(('1', 'Single'), ('2', 'Married')))
    gender = serializers.ChoiceField(allow_blank=True, choices=(('M', 'Male'), ('F', 'Female')))
    nationality = serializers.CharField(allow_blank=True, max_length=254)

    class Meta:
        model = models.User
        fields = ('marital_status', 'gender', 'nationality')

class IsCompleteSerializer(serializers.ModelSerializer):
    """
    Serializer for checking if user has completed investor_info, identity_info, contact_info, bank_info, nominee_info
    and has declared and accepted the terms and conditions
    """

    class Meta:
        model = models.User
        fields = ('is_investor_info', 'is_identity_info', 'is_contact_info', 'is_bank_info', 'is_nominee_info',
                  'is_declaration', 'is_terms')


class IsCompletePostSerializer(serializers.ModelSerializer):
    """
    For declaring and accepting the terms and conditions
    """

    class Meta:
        model = models.User
        fields = ('is_declaration', 'is_terms')


class ContactInfoContinueSerializer(serializers.ModelSerializer):
    """
    This serializer is used to set the address_proof_type and front_image together
    and also sets the back image for the contact info if provided.
    """

    class Meta:
        model = models.ContactInfo
        fields = ('address_proof_type', 'permanent_address_proof_type', 'front_image', 'back_image', 'permanent_front_image', 'permanent_back_image')


class NomineeInfoSerializer(serializers.ModelSerializer):
    """
    This serializer is used to get and display nominee info.
    """
    nominee_address = AddressSerializer()

    class Meta:
        model = models.NomineeInfo
        exclude = ('user', 'id')


class AppointmentDetailsGetSerializer(serializers.ModelSerializer):
    """
    The appointment_details serializer.
    """
    address = AddressSerializer()

    class Meta:
        model = models.AppointmentDetails
        exclude = ('user', 'id', 'status')


class SetProcessChoiceSerializer(serializers.ModelSerializer):
    """
    The process_choice is set in the User model.
    """

    class Meta:
        model = models.User
        fields = ('process_choice', )


class InvestorBankInfoGetSerializer(serializers.ModelSerializer):
    """
    Serializer for investor account info get api
    """
    ifsc_code = external_api_serializers.BankInfoGetWithIFSCSerializer()

    class Meta:
        model = models.InvestorBankDetails
        fields = ('account_number', 'account_holder_name', 'account_type', 'sip_check', 'ifsc_code',
                  'bank_cheque_image', )


class InvestorBankInfoPostSerializer(serializers.ModelSerializer):
    """
    Serializer for investor account info get api
    """

    class Meta:
        model = models.InvestorBankDetails
        fields = ('account_number', 'account_holder_name', 'account_type', 'sip_check',)


class ForgotPasswordCheckOTPSerializer(serializers.Serializer):
    """
    Serializer fot forgot password check otp api
    """
    email = serializers.EmailField(required=True)
    otp = serializers.IntegerField(required=True)


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    User information Get and put API
    """
    name = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = models.User
        fields = ('name', 'phone_number')
