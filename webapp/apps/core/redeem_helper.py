from django.db.models import F
from datetime import datetime
from django.db.models import Sum
import logging
from core import models
from core import funds_helper
from core import portfolio_helper
from core.portfolio_helper import PortfolioHelper


class RedeemHelper(object):
    
    error_logger = logging.getLogger('django.error')
    
    def __init__(self):
        super(RedeemHelper, self).__init__()

    @staticmethod
    def get_units_redeemed(portfolio_item, folio_number=None):
        if folio_number:
            unit_redeemed__sum = models.FundRedeemItem.objects.filter(
                                portfolio_item__id=portfolio_item.id, is_verified=True, folio_number=folio_number).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
            unverified_amount_redeemed__sum = models.FundRedeemItem.objects.filter(
                portfolio_item__id=portfolio_item.id, is_verified=False, is_cancelled=False, folio_number=folio_number
            ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']
        else:
            unit_redeemed__sum = models.FundRedeemItem.objects.filter(
                                portfolio_item__id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
            unverified_amount_redeemed__sum = models.FundRedeemItem.objects.filter(
                portfolio_item__id=portfolio_item.id, is_verified=False, is_cancelled=False
            ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']
            


        if unit_redeemed__sum is None:
            unit_redeemed__sum = 0
        unverified_unit_redeemed = 0
        if unverified_amount_redeemed__sum is not None and unverified_amount_redeemed__sum > 0:
            nav = funds_helper.FundsHelper.get_current_nav(portfolio_item.fund.id)
            if nav and nav > 0:
                unverified_unit_redeemed = unverified_amount_redeemed__sum/nav

        return unit_redeemed__sum + unverified_unit_redeemed
    
    @staticmethod
    def get_redeemable_units(portfolio_item, folio_number=None):
        if folio_number:
            unit_alloted_sum = models.FundOrderItem.objects.filter(portfolio_item=portfolio_item, is_cancelled=False, is_verified=True, 
                                                               unit_alloted__gt=F('units_redeemed'), folio_number=folio_number
                                            ).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
        else:
            unit_alloted_sum = models.FundOrderItem.objects.filter(portfolio_item=portfolio_item, is_cancelled=False, is_verified=True, 
                                                               unit_alloted__gt=F('units_redeemed')
                                            ).aggregate(Sum('unit_alloted'))['unit_alloted__sum']

        if not unit_alloted_sum:
            unit_alloted_sum = 0
            
        unit_redeemed_sum = RedeemHelper.get_units_redeemed(portfolio_item, folio_number)
        
        return (unit_alloted_sum - unit_redeemed_sum)

    @staticmethod
    def calculate_invested_redeem_amount(fund_redeem_item):
        return 0
    
    @staticmethod
    def generate_redeem_for_goal(goal, all_unit_funds, amount_funds):
        error_logger = logging.getLogger('django.error')
        fund_redeem_items = []
        try:
            for amount_fund in amount_funds:
                portfolio_item = models.PortfolioItem.objects.get(fund_id=amount_fund['fund_id'], goal=goal)
                previous_units_redeemed = RedeemHelper.get_units_redeemed(portfolio_item)

                redeem_items = {}
                # Redeem from lumpsum and then sip, use folio numbers from each fund order item 
                redeem_amount = float(amount_fund['redeem_amount'])
                
                lumpsum_order, sip_order = portfolio_helper.PortfolioHelper.get_first_lumpsum_and_sip(portfolio_item)
                folio_number = ""
                if (lumpsum_order and not lumpsum_order.folio_number) or (sip_order and not sip_order.folio_number):
                    folio_number = funds_helper.FundsHelper.get_folio_number(goal.user, portfolio_item.fund)
                    if lumpsum_order:
                        lumpsum_order.folio_number = lumpsum_order.folio_number or folio_number
                    
                    if sip_order:
                        sip_order.folio_number = sip_order.folio_number or folio_number
                    
                if lumpsum_order and lumpsum_order.unit_alloted > previous_units_redeemed:
                    nav = funds_helper.FundsHelper.get_current_nav(portfolio_item.fund.id)
                    lumpsum_value = (lumpsum_order.unit_alloted - previous_units_redeemed) * nav
                    redeem_items[lumpsum_order.folio_number] = min(lumpsum_value, redeem_amount)
                    redeem_amount = redeem_amount - redeem_items[lumpsum_order.folio_number]
                 
                if redeem_amount > 0:
                    if sip_order:
                        if redeem_items.get(sip_order.folio_number):
                            redeem_items[sip_order.folio_number] += redeem_amount
                        else:
                            redeem_items[sip_order.folio_number] = redeem_amount

                # TODO : invested_redeem_amount
                for folio_number in redeem_items:
                    fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    folio_number = folio_number, 
                                                                    redeem_amount=redeem_items[folio_number])
                    fund_redeem_items.append(fund_redeem_item)

            for all_unit_fund in all_unit_funds:
                portfolio_item = models.PortfolioItem.objects.get(fund_id=all_unit_fund['fund_id'], goal=goal)

                redeem_items = {}
                lumpsum_order, sip_order = portfolio_helper.PortfolioHelper.get_first_lumpsum_and_sip(portfolio_item)

                folio_number = ""
                if (lumpsum_order and not lumpsum_order.folio_number) or (sip_order and not sip_order.folio_number):
                    folio_number = funds_helper.FundsHelper.get_folio_number(goal.user, portfolio_item.fund)
                    if lumpsum_order:
                        lumpsum_order.folio_number = lumpsum_order.folio_number or folio_number
                    
                    if sip_order:
                        sip_order.folio_number = sip_order.folio_number or folio_number

                if lumpsum_order and lumpsum_order.unit_alloted > lumpsum_order.units_redeemed:    
                    redeem_items[lumpsum_order.folio_number] = True

                if sip_order:
                    redeem_items[sip_order.folio_number] = True
                    
                for folio_number in redeem_items:
                    fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    folio_number = folio_number, 
                                                                    unit_redeemed=0.0, is_all_units_redeemed=True)
                    fund_redeem_items.append(fund_redeem_item)
                    
        except Exception as e:
            error_logger.error("Error generation fund redeem items: " + str(e))
            
        return fund_redeem_items
