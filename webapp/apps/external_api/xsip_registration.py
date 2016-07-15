from core import utils, models
from . import constants as cons

from collections import OrderedDict
from datetime import datetime
import os, time


def generate_user_pipe_file(user, order_items):
    """
    This function generates a pipe separated file for bulk order entry.
    :param order_items: list of order_items for that order_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the bulk order entry
    """
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    bulk_user_pipe_file_name = "bulk_user_pipe" + timestamp + ".txt"
    outfile = open(output_path + bulk_user_pipe_file_name, "w")
    for i, item in enumerate(order_items):
        neft_code = ''
        if item.portfolio_item.fund.bse_neft_scheme_code:
            neft_code = item.portfolio_item.fund.bse_neft_scheme_code
        rgts_code = ""
        if item.portfolio_item.fund.bse_rgts_scheme_code:
            rgts_code = item.portfolio_item.fund.bse_rgts_scheme_code
        agreed_sip = 0
        sip_tenure = user.get_sip_tenure(item.portfolio_item.portfolio)
        installment_no = 0 if sip_tenure is None else (sip_tenure * 12)
        if item.agreed_sip:
            agreed_sip = item.agreed_sip
        internal_ref_no = ""
        if item.internal_ref_no:
            internal_ref_no = item.internal_ref_no
        mandate_id = ""
        if user.mandate_reg_no:
            mandate_id = user.mandate_reg_no
        amc_code = ""
        if item.portfolio_item.fund.amc_code:
            amc_code = item.portfolio_item.fund.amc_code
        fund_id = ""
        start_date = ""
        if item.portfolio_item.fund.id:
            fund_id = item.portfolio_item.fund.id
            start_date = utils.get_valid_start_date(fund_id).strftime("%d/%m/%Y")

        fund_house = ""
        folio_number = ""
        if item.portfolio_item.fund.fund_house:
            fund_house = item.portfolio_item.fund.fund_house
            try:
                f_number = models.FolioNumber.objects.get(user=user, fund_house=fund_house).folio_number
                if f_number:
                    folio_number = f_number
            except models.FolioNumber.DoesNotExist:
                folio_number = ""

        bulk_user_dict = OrderedDict([('AMC Code', amc_code),
                                      ('SCHEME CODE', neft_code if item.order_amount < 200000 else rgts_code),
                                      ('Client Code', str(user.finaskus_id)),
                                      ('Internal Ref No.', internal_ref_no),
                                      ('Trans Mode ', cons.Accept_Mode),
                                      ('DP TXN Mode', cons.DP_TXN_MODE),
                                      ('Start Date', start_date),
                                      ('Frequency Type', cons.Frequency_Type),
                                      ('Frequency Allowed', cons.Frequency_Allowed),
                                      ('Installment Amount', str(agreed_sip)),
                                      ('Status', cons.Xsip_status),
                                      ('Member Code', cons.MEMBER_CODE),
                                      ('Folio No.', str(folio_number)),
                                      ('SIP Remarks', ''),
                                      ('Installment No.', str(installment_no)),
                                      ('Brokerage', cons.Brokerage_money),
                                      ('Mandate ID', mandate_id),
                                      ('Sub Broker ARN Code', ''),
                                      ('EUIN Number', cons.Order_EUIN_Number),
                                      ('EUIN Declaration', cons.Order_EUIN_declaration),
                                      ('DPC Flag', cons.Order_DPC_Flag),
                                      ('First Order Today', cons.First_Order_Today), ])
        if int(agreed_sip) > 0:
            outfile.write("|".join(bulk_user_dict.values()))
            if i < len(order_items) - 1:
                outfile.write("\r")
            bulk_user_dict.clear()
    outfile.close()
    return output_path + bulk_user_pipe_file_name
