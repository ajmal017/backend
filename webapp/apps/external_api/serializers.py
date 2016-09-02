from rest_framework import serializers

from . import models


class PinCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for PinCode
    """
    class Meta:
        model = models.Pincode
        fields = '__all__'


class BankDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer to populate data into bank detial model
    """
    class Meta:
        model = models.BankDetails
        fields = '__all__'


class BankInfoGetSerializer(serializers.ModelSerializer):
    """
    Serializer to return data for bank info
    """
    is_bank_supported = serializers.BooleanField(required=True)
    class Meta:
        model = models.BankDetails
        fields = ('name', 'bank_branch', 'address', 'city')


class BankInfoGetWithIFSCSerializer(serializers.ModelSerializer):
    """
    Serializer to return data for bank info with ifsc code
    """
    class Meta:
        model = models.BankDetails
        fields = ('name', 'bank_branch', 'address', 'city', 'ifsc_code')

