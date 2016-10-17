from external_api.utils import generate_tiff
from profiles import models

from num2words import num2words
from collections import OrderedDict
from datetime import datetime
from subprocess import call
from fdfgen import forge_fdf
from external_api import constants as cons
import os
import time


def generate_bank_mandate_file(user_id, bank_mandate):
    """
    This function generates a pipe separated file for bank mandate.
    :param order_items: list of order_items for that order_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the bank mandate
    """
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    bank_mandate_pipe_file_name = "bank_mandate_pipe" + timestamp + ".txt"
    outfile = open(output_path + bank_mandate_pipe_file_name, "w")
    user = models.User.objects.get(id=user_id)
    bank_mandate_dict = OrderedDict([('Member Code', cons.MEMBER_CODE),
                                     ('UCC', str(user.finaskus_id)),
                                     ('Amount', str(bank_mandate.mandate_amount)),
                                     ('IFSC Code', bank_mandate.mandate_bank_details.ifsc_code),
                                     ('Account Number', bank_mandate.mandate_bank_details.account_number), ])
    outfile.write("|".join(bank_mandate_dict.values()))
    outfile.write("\r")
    outfile.close()
    return output_path + bank_mandate_pipe_file_name


def generate_bank_mandate_pdf(user_id, bank_mandate):
    """
    This function fills the bank mandate pdf with pertinent user's data.
    :param user_id: The id of the user for whom the mandate is generated.
    :return: path of the generated mandate pdf.
    """

    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    curr_date = datetime.now()

    if not user.mandate_reg_no:
        return None, "Mandate Registration Number Missing"
    
    mandate_dict = {
        'MandateAccountHolderName': bank_mandate.bank_details.account_holder_name,
        'MandateAmountNumber': bank_mandate.mandate_amount,
        'MandateAmountWords': str(num2words(bank_mandate.mandate_amount, lang="en_IN")) + " ONLY",
        'MandateBank': bank_mandate.bank_details.ifsc_code.name,
        'MandateBankACNumber': bank_mandate.bank_details.account_number,
        'MandateCreate': True,
        'MandateDate-dd': curr_date.strftime("%d"),
        'MandateDate-mm': curr_date.strftime("%m"),
        'MandateDate-yyyy': curr_date.strftime("%Y"),
        'MandateEmailID': contact.email,
        'MandateIFSC': bank_mandate.bank_details.ifsc_code.ifsc_code,
        'MandatePeriodFrom-dd': bank_mandate.bank_details.strftime("%d"),
        'MandatePeriodFrom-mm': bank_mandate.bank_details.strftime("%m"),
        'MandatePeriodFrom-yyyy': bank_mandate.bank_details.strftime("%Y"),
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
    
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    bank_mandate_pdf_path = base_dir + '/bse_docs/'
    output_path = base_dir + '/webapp/static/'

    call(("pdftk " + bank_mandate_pdf_path + "BankMandate.pdf fill_form %s output " % temp_file_name + output_path +
          "%s flatten" % out_file_name
          ).split())

    call(("rm " + temp_file_name).split())

    return output_path + out_file_name, None


def generate_bank_mandate_tiff(user_id):
    """
    This function fills the bank mandate pdf with pertinent user's data and convert it into tiff format.
    :param user_id: The id of the user for whom the mandate is generated.
    :return: path of the generated mandate tiff.
    """
    pdf_path = generate_bank_mandate_pdf(user_id)
    output_path = os.path.dirname(pdf_path)
    final_tiff_file_name = generate_tiff(pdf_path, bank_cheque_image = None)
    return output_path + final_tiff_file_name
