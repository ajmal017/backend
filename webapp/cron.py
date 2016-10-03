from django.db.models import Min

from external_api import morningstar
from core import utils, models
from profiles import utils as profile_utils

import logging
from datetime import datetime, date


def generate_log_message(received_value, table_type, expected_value, logger):
    """
    generates log for cron jobs
    :param received_value: the number of funds/indices/categories from morning star
    :param expected_value: the expected number of funds/indices/categories from morning star
    :param table_type: the table for which log is being generated
    :param logger: the logger which we need to use
    :return:
    """

    logger.info(table_type + ' expected  ' + str(expected_value) + ' received ' + str(received_value))
    logger.info(table_type + ' was updated on date ' + str(date.today()))


def daily_cron():
    """
    Cron for getting morning star data on daily basis
    :return:
    """
    profile_utils.send_daily_mails_for_bse_registration()
    morningstar_object = morningstar.MorningStarBackend()
    mail_logger = logging.getLogger('django.info')
    is_error, errors = False, ''
    try:
        generate_log_message(morningstar_object.get_data_points_for_fund_data_points_change_daily(), 'daily', 56,
                             mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_data_points_for_fund_data_points_change_daily; '
        errors += error_entry
    try:
        generate_log_message(morningstar_object.get_daily_nav_for_indices_new(), 'index_nav', 14, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_daily_nav_for_indices_new; '
        errors += error_entry
    try:
        generate_log_message(morningstar_object.get_daily_nav_categories_new(), 'category_nav', 8, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_daily_nav_categories_new; '
        errors += error_entry

    # try:
    #     generate_log_message(utils.generate_total_xirr(), 'portfolio', 0, mail_logger)
    # except Exception as e:
    #     is_error = True
    #     error_entry = str(e) + ' get xirr of user having portfolio and not invested; '
    #     errors += error_entry

    try:
        generate_log_message(utils.generate_units_allotment(), 'fund_order_items', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + 'generate units of fund order and redeem items; '
        errors += error_entry

    try:
        generate_log_message(utils.set_xirr_values_for_users_not_having_investment(), 'xirr non-invested', 0,
                             mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' XIRR for non invested users '
        errors += error_entry

    try:
        generate_log_message(utils.set_xirr_values_for_users_having_investment(), 'xirr-invested', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' XIRR for invested users'
        errors += error_entry

    try:
        generate_log_message(utils.tracking_funds_bse_nse(), 'Tracking MS', 58, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + 'tracking_bse'
        errors += error_entry

    try:
        generate_log_message(utils.store_most_popular_fund_data(), 'updating most pouplar funds', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + 'updating most pouplar funds'
        errors += error_entry

    try:
        count = 0
        order_details = models.OrderDetail.objects.filter(order_status=2).distinct('user')
        for user in order_details:
            order_ids = models.OrderDetail.objects.filter(user=user.user, order_status=2).values_list('id', flat=True)
            inception_date = models.FundOrderItem.objects.filter(orderdetail__in=order_ids).aggregate(Min('allotment_date'))
            if inception_date["allotment_date__min"]:
                count +=1
                dashboard_date = utils.get_dashboard_change_date()
                amount = utils.get_current_invested_value_date(
                    datetime(dashboard_date.year, dashboard_date.month, dashboard_date.day), user.user)
                if inception_date["allotment_date__min"] == dashboard_date:
                    amount['xirr'] = 0.0
                if amount['xirr'] == "inf" or type(amount['xirr']) == complex:
                    xirr = 0.0
                else:
                    xirr = round(amount['xirr']*100, 1)
                models.PortfolioPerformance.objects.update_or_create(date=dashboard_date, user=user.user, defaults={
                    'current_amount': amount['current_amount'], 'invested_amount': amount['invested_amount'],
                    'xirr': xirr})
        generate_log_message(count, 'Portfolio tracker cron', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + 'generates invested, current amount and xirr of user on particular date; '
        errors += error_entry

    try:
        generate_log_message(profile_utils.update_kyc_status(), 'update_kyc_status', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' update_kyc_status; '
        errors += error_entry

    if is_error:
        mail_logger.info(errors)


def daily_once_cron():
    """
    :return:
    """
    mail_logger = logging.getLogger('django.info')
    is_error, errors = False, ''

    try:
        generate_log_message(utils.create_order_items_based_on_next_allotment_date(), 'order_items', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' create_order_items_based_on_next_allotment_date; '
        errors += error_entry

    try:
        generate_log_message(utils.reminder_next_sip_allotment(), 'SIP_Reminder', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' reminder_next_sip_allotment; '
        errors += error_entry
    
    if is_error:
        mail_logger.info(errors)

def weekly_once_cron():
    """
    :return:
    """
    mail_logger = logging.getLogger('django.info')
    is_error, errors = False, ''

    try:
        generate_log_message(utils.get_portfolio_dashboard(), 'get_portfolio', 0, mail_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_portfolio_dashboard; '
        errors += error_entry
    
    if is_error:
        mail_logger.info(errors)

def monthly_cron():
    """
    Cron for getting morning star data on monthly basis
    :return:
    """
    morningstar_object = morningstar.MorningStarBackend()
    monthly_logger = logging.getLogger('django.info')
    is_error, errors = False, ''
    try:
        generate_log_message(morningstar_object.get_data_points_for_fund_data_points_change_monthly(), 'monthly', 30,
                             monthly_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_data_points_for_fund_data_points_change_monthly; '
        errors += error_entry
    try:
        generate_log_message(morningstar_object.get_data_points_for_equity(), 'equity', 20, monthly_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_data_points_for_equity; '
        errors += error_entry
    try:
        generate_log_message(morningstar_object.get_data_points_for_sectors(), 'sectors', 20, monthly_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_data_points_for_sectors; '
        errors += error_entry
    try:
        generate_log_message(morningstar_object.get_data_points_for_debt(), 'debt', 10, monthly_logger)
    except Exception as e:
        is_error = True
        error_entry = str(e) + ' get_data_points_for_debt; '
        errors += error_entry
    if is_error:
        monthly_logger.info(errors)
