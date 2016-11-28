from django.db.models import F
from datetime import datetime
from django.db.models import Sum
import logging
from core import models
from core import funds_helper
from core import portfolio_helper


class RedeemHelper(object):
    
    error_logger = logging.getLogger('django.error')
    
    def __init__(self):
        super(RedeemHelper, self).__init__()

    @staticmethod
    def get_units_redeemed(portfolio_item):
        unit_redeemed__sum = models.FundRedeemItem.objects.filter(
                                portfolio_item_id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']

        unverified_amount_redeemed__sum = models.FundRedeemItem.objects.filter(
            portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
        ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']

        unverified_unit_redeemed = 0
        if unverified_amount_redeemed__sum > 0:
            nav = funds_helper.FundsHelper.get_current_nav(portfolio_item.fund.id)
            if nav and nav > 0:
                unverified_unit_redeemed = unverified_amount_redeemed__sum/nav

        return unit_redeemed__sum + unverified_unit_redeemed
    
    @staticmethod
    def calculate_invested_redeem_amount(fund_redeem_item):
        return 0
    
    @staticmethod
    def generate_redeem_for_goal(goal, all_unit_funds, amount_funds):
        error_logger = logging.getLogger('django.error')
        fund_redeem_items = []
        try:
            for amount_fund in amount_funds:
                portfolio_item = models.PortfolioItem.objects.get(fund_id=amount_fund.fund_id, goal=goal)
                previous_units_redeemed = RedeemHelper.get_units_redeemed(portfolio_item)

                redeem_items = {}
                # Redeem from lumpsum and then sip, use folio numbers from each fund order item 
                redeem_amount = amount_fund.redeem_amount
                
                lumpsum_order, sip_order = portfolio_helper.PortfolioHelper.get_first_lumpsum_and_sip(portfolio_item)

                if lumpsum_order and lumpsum_order.unit_alloted > previous_units_redeemed:
                    nav = funds_helper.FundsHelper.get_current_nav(portfolio_item.fund.id)
                    lumpsum_value = (lumpsum_order.unit_alloted - previous_units_redeemed) * nav
                    redeem_items[lumpsum_order.folio_number] = min(lumpsum_value, redeem_amount)
                    redeem_amount = redeem_amount - redeem_items[lumpsum_order.folio_number]
                 
                if redeem_amount > 0:
                    if sip_order:
                        redeem_items[sip_order.folio_number] += redeem_amount 

                # TODO : invested_redeem_amount
                for folio_number, amount in redeem_items:
                    fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    folio_number = folio_number, 
                                                                    redeem_amount=amount)
                    fund_redeem_items.append(fund_redeem_item)

            for all_unit_fund in all_unit_funds:
                portfolio_item = models.PortfolioItem.objects.get(fund_id=all_unit_fund.fund_id, goal=goal)

                redeem_items = []
                lumpsum_order, sip_order = portfolio_helper.PortfolioHelper.get_first_lumpsum_and_sip(portfolio_item)

                if lumpsum_order and lumpsum_order.unit_alloted > lumpsum_order.units_redeemed:    
                    redeem_items.append(lumpsum_order.folio_number)

                if sip_order:
                    redeem_items.append(sip_order.folio_number)
                    
                for folio_number in redeem_items:
                    fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    folio_number = folio_number, 
                                                                    unit_redeemed=0.0, is_all_units_redeemed=True)
                    fund_redeem_items.append(fund_redeem_item)
                    
        except Exception as e:
            error_logger.error("Error generation fund redeem items: " + str(e))
            
        return fund_redeem_items