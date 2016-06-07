from rest_framework import serializers

from . import models


class TransactionSerializer(serializers.Serializer):
    """
    Serializer for transaction api
    """
    txn_amount = serializers.CharField(max_length=12, required=True)