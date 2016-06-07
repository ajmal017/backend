from django import template

from api import utils as api_utils
from core import constants
from core.models import FundOrderItem, FundRedeemItem

register = template.Library()


@register.filter(name='get_order_items')
def get_order_items(value):
    try:
        item = FundOrderItem.objects.get(id=value)
        return item
    except FundOrderItem.DoesNotExist:
        return None

@register.filter(name='get_redeem_details')
def get_redeem_details(value):
    try:
        item = FundRedeemItem.objects.get(id=value)
        return item
    except FundRedeemItem.DoesNotExist:
        return None
