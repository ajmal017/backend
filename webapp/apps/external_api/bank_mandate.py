from external_api.utils import generate_tiff
from profiles import models
from external_api import helpers

from num2words import num2words
from collections import OrderedDict
from datetime import datetime
from subprocess import call
from fdfgen import forge_fdf
from . import constants as cons
import os
import time

class BankMandateHelper(object):
    def is_new_mandate_required(self, order_detail, create_new=False):
        if order_detail:
            mandate_vendor = order_detail.vendor
        
        if not mandate_vendor:
            mandate_vendor = helpers.get_exchange_vendor_helper().get_active_vendor()
            
        return False;
    
    
def generate_bank_mandate_file(user, mandate_amount):
    """
    This function generates a pipe separated file for bank mandate.
    :param order_items: list of order_items for that order_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the bank mandate
    """
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    bank_mandate_pipe_file_name = "bank_mandate_pipe" + timestamp + ".txt"
    outfile = open(output_path + bank_mandate_pipe_file_name, "w")
    bank_mandate_dict = OrderedDict([('Member Code', cons.MEMBER_CODE),
                                     ('UCC', str(user.finaskus_id)),
                                     ('Amount', str(mandate_amount)),
                                     ('IFSC Code', user.investorbankdetails.ifsc_code.ifsc_code),
                                     ('Account Number', user.investorbankdetails.account_number), ])
    outfile.write("|".join(bank_mandate_dict.values()))
    outfile.write("\r")
    outfile.close()
    return output_path + bank_mandate_pipe_file_name


def generate_bank_mandate_pdf(user_id, mandate_amount):
    """
    This function fills the bank mandate pdf with pertinent user's data.
    :param user_id: The id of the user for whom the mandate is generated.
    :return: path of the generated mandate pdf.
    """

    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    if not user.mandate_reg_no:
        return None, "Mandate Registration Number Missing"
    
    mandate_dict = {
        'MandateAccountHolderName': investor_bank.account_holder_name,
        'MandateAmountNumber': mandate_amount,
        'MandateAmountWords': str(num2words(mandate_amount, lang="en_IN")) + " ONLY",
        'MandateBank': investor_bank.ifsc_code.name,
        'MandateBankACNumber': investor_bank.account_number,
        'MandateCreate': True,
        'MandateDate-dd': curr_date.strftime("%d"),
        'MandateDate-mm': curr_date.strftime("%m"),
        'MandateDate-yyyy': curr_date.strftime("%Y"),
        'MandateEmailID': contact.email,
        'MandateIFSC': investor_bank.ifsc_code.ifsc_code,
        'MandatePeriodFrom-dd': curr_date.strftime("%d"),
        'MandatePeriodFrom-mm': curr_date.strftime("%m"),
        'MandatePeriodFrom-yyyy': curr_date.strftime("%Y"),
        'MandatePhoneNo': contact.phone_number,
        'MandateReferenceNo': user.mandate_reg_no,
        'MandateUCC': investor.user.finaskus_id,
    }

    for key, value in mandate_dict.items():
        if value is None:
            mandate_dict[key] = ""
        if value is True:
            mandate_dict[key] = "Yes"
        if value is False:
            mandate_dict[key] = "Off"

    for key, value in mandate_dict.items():
        if value not in ("", "Yes", "Off"):
            if type(value) == str:
                if "@" in value:
                    continue
            mandate_dict[key] = str(value).upper()

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    fields = [(key, value) for key, value in mandate_dict.items()]
    fdf = forge_fdf("", fields, [], [], [])
    temp_file_name = "mandate_temp" + timestamp + ".fdf"
    out_file_name = "mandate_out" + timestamp + ".pdf"
    fdf_file = open(temp_file_name, "wb")
    fdf_file.write(fdf)
    fdf_file.close()
    
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    bank_mandate_pdf_path = base_dir + '/bse_docs/'
    output_path = base_dir + '/webapp/static/'

    call(("pdftk " + bank_mandate_pdf_path + "BankMandate.pdf fill_form %s output " % temp_file_name + output_path +
          "%s flatten" % out_file_name
          ).split())

    call(("rm " + temp_file_name).split())

    return output_path + out_file_name, None

