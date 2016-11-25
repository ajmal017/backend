import logging
from core import models


class PortfolioHelper(object):
    
    error_logger = logging.getLogger('django.error')
    
    def __init__(self):
        super(PortfolioHelper, self).__init__()

    @staticmethod
    def get_first_lumpsum_and_sip(portfolio_item):
        """
        returns latest nav date for funds
        :return:the minimum date fron funds
        """
        fund_order_items = models.FundOrderItem.objects.filter(portfolio_item=portfolio_item, order_detail__is_lumpsum=True, is_verified=True, is_cancelled=False)

        try:
            lumpsum_order = fund_order_items.filter(agreed_lumpsum__gt=0).first()
        except:
            lumpsum_order = None

        try:
            sip_order = fund_order_items.filter(agreed_sip__gt=0).first()
        except:
            sip_order = None
        
        return lumpsum_order, sip_order
    
    @staticmethod 
    def get_all_transactions(portfolio_item):
        transactions = []
        
        order_items = models.FundOrderItem.objects.filter(portfolio_item=portfolio_item, is_cancelled=False).order_by("created_at")
        redeem_items = models.FundRedeemItem.objects.filter(portfolio_item=portfolio_item, is_cancelled=False).order_by("created_at")
        
        transactions.append(order_items)
        transactions.append(redeem_items)
        
        return transactions