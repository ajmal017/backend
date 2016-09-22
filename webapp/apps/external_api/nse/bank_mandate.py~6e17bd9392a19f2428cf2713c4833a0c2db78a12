from external_api.utils import generate_tiff, embed_images
from profiles import models, utils
from external_api import constants

from num2words import num2words
from collections import OrderedDict
from datetime import datetime
from subprocess import call
from fdfgen import forge_fdf
from external_api import constants as cons
import os
import time


def generate_bank_mandate_tiff(user_id, **kwargs):
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

    mandate_amount = kwargs.get('mandate_amount')

    mandate_dict = {
        'MandateAccountHolderName': investor_bank.account_holder_name,
        'MandateAmountNumber': mandate_amount,
        'MandateAmountWords': str(num2words(mandate_amount, lang="en_IN")) + " ONLY",
        'MandateBank': investor_bank.ifsc_code.name,
        'MandateBankACNumber': investor_bank.account_number,
        'MandateBankACType': investor_bank.account_type,
        'MandateDate-dd': curr_date.strftime("%d"),
        'MandateDate-mm': curr_date.strftime("%m"),
        'MandateDate-yyyy': curr_date.strftime("%Y"),
        'MandateIFSC': investor_bank.ifsc_code.ifsc_code,
        'MandatePeriodFrom-dd': curr_date.strftime("%d"),
        'MandatePeriodFrom-mm': curr_date.strftime("%m"),
        'MandatePeriodFrom-yyyy': curr_date.strftime("%Y")
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
    bank_mandate_pdf_path = base_dir + '/nse_docs/'
    output_path = base_dir + '/webapp/static/'

    call(("pdftk " + bank_mandate_pdf_path + "BankMandate.pdf fill_form %s output " % temp_file_name + output_path +
          "%s flatten" % out_file_name
          ).split())

    call(("rm " + temp_file_name).split())

    prefix = "webapp"  # prefix is needed to access the images from media directory.

    # the list of images to be embedded into the pdf follows
    user_signature = prefix + user.signature.url if user.signature != "" else constants.DEFAULT_IMAGE  # signature_image location.
    list_of_embeddable_images = [user_signature, ]

    # list of individual image type/size (passport/signature) they are based on international standards.
    image_sizes = [constants.TIFF_SIGNATURE_SIZE, ]

    bank_mandate = "bank_mandate" + timestamp + ".pdf"

    dest = output_path + bank_mandate  # the final pdf with all images in place.
    exist = output_path + out_file_name   # the source pdf without the images.
    coords = [(125, 24), ]  # the lower left bottom corner
    #  co-ordinates for each of the images.

    target_pages = (0, )  # pages of the existing/source pdf into which the images from the images list must be
    #  embedded onto

    images_count_each_page = [1, ]  # number of images on each of the target pages.

    # following makes a call to the embed images function in the utils
    embed_images(list_of_embeddable_images, image_sizes, coords, target_pages, images_count_each_page, dest, exist)
    # following generates the tiff file.

    final_tiff_file_name = generate_tiff(output_path + bank_mandate, investor_bank.bank_cheque_image)
    return output_path + final_tiff_file_name
