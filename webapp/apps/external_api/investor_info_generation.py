from django.db.models import Sum

from fdfgen import forge_fdf
from num2words import num2words

from profiles import models, utils
from core.models import PortfolioItem
from external_api.kyc_generator import kyc_fdf_generator
from .models import Pincode
from .utils import embed_images
from external_api import constants as cons

from datetime import datetime
import time
from subprocess import call
import os


def investor_info_generator(user_id):
    """
    :param user_id: the id of user for which we need to generate investor form
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    if nominee.nominee_address == None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    mandate_amount_no = max(utils.get_investor_mandate_amount(user), 100000)

    investor_dict = {
        # 'MandateDebitTypeMaxAmount': True,
        # 'MandateFreqAsWhenPresented': True,
        # 'MandateUntilCancelled': True,  # TODO: verify with rashmi
        'DebitSB': True,  # TODO: Check with rashmi
        'AccountNumber': investor_bank.account_number,
        'AccountType': investor_bank.get_account_type_display(),
        'ApplicantName': investor.applicant_name,
        'BankName': investor_bank.ifsc_code.name,
        'BranchName': investor_bank.ifsc_code.bank_branch,
        'CorrespondenceAddress1': contact.communication_address.address_line_1,
        'CorrespondenceAddress2': contact.communication_address.address_line_2,
        'CorrespondenceAddressCity': contact.communication_address.pincode.city,
        'CorrespondenceAddressState': contact.communication_address.pincode.state,
        'CorrespondenceAddressCountry': user.nationality,
        'CorrespondenceAddressPincode': contact.communication_address.pincode.pincode,
        'PermanentAddressSameAsCorrespondenceAddress': True if contact.address_are_equal else False,
        'PermanentAddress1': contact.permanent_address.address_line_1 if not contact.address_are_equal else None,
        'PermanentAddress2': contact.permanent_address.address_line_2 if not contact.address_are_equal else None,
        'PermanentAddressCity': contact.permanent_address.pincode.city if not contact.address_are_equal else None,
        'PermanentAddressState': contact.permanent_address.pincode.state if not contact.address_are_equal else None,
        'PermanentAddressPincode': contact.permanent_address.pincode.pincode if not contact.address_are_equal else None,
        'PermanentAddressCountry': user.nationality if not contact.address_are_equal else None,
        'DateofBirth': investor.dob.strftime("%d/%m/%Y"),
        'EmailID': investor.user.email,
        'FinaskusInvestorID': user.finaskus_id,
        'GrossAnnualIncome': investor.get_income_display(),
        'IFSCCode': investor_bank.ifsc_code.ifsc_code,
        'InvestorsRelationwithNominee': nominee.get_relationship_with_investor_display() if nominee else None,
        'MandateAccountHolderName': investor_bank.account_holder_name,
        'MandateAmountNumber': mandate_amount_no,
        'MandateAmountWords': str(num2words(mandate_amount_no, lang="en_IN")) + " ONLY",
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
        'Mobile': contact.phone_number,
        'NameofGuardian': nominee.guardian_name if nominee else None,
        'NominationNotRequired': nominee.nominee_absent,
        'NomineeAddressSameAsInvestorAddress': True if nominee and nominee.address_are_equal else False,
        'NomineeAddress1': nominee.nominee_address.address_line_1,
        'NomineeAddress2': nominee.nominee_address.address_line_2,
        'NomineeAddressCity': nominee.nominee_address.pincode.city,
        'NomineeAddressCountry': user.nationality,
        'NomineeAddressPinCode': nominee.nominee_address.pincode,
        'NomineeAddressState': nominee.nominee_address.pincode.state,
        'NomineeName': nominee.nominee_name if nominee else None,
        'Occupation': investor.get_occupation_type_display() if investor.occupation_type != "OTH" else investor.occupation_specific,
        'OnlineApplicationDate': curr_date.strftime("%d/%m/%Y"),
        'PAN': investor.pan_number,
        'Place': contact.communication_address.pincode.city,
        'PoliticalStatusExposed': True if investor.political_exposure == 2 else False,
        'PoliticalStatusRelated': True if investor.political_exposure == 3 else False,
        'ResidentStatus': investor.investor_status,
        'TaxPayer': investor.other_tax_payer,
        'UMRN': None}

    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ""
        if value is True:
            investor_dict[key] = "Yes"
        if value is False:
            investor_dict[key] = "Off"

    for key, value in investor_dict.items():
        if value not in ("", "Yes", "Off"):
            if type(value) == str:
                if "@" in value:
                    continue
            investor_dict[key] = str(value).upper()

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    fields = [(key, value) for key, value in investor_dict.items()]
    fdf = forge_fdf("", fields, [], [], [])
    temp_file_name = "temp" + timestamp + ".fdf"
    out_file_name = "out" + timestamp + ".pdf"
    fdf_file = open(temp_file_name, "wb")
    fdf_file.write(fdf)
    fdf_file.close()

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    investor_pdf_path = base_dir + '/bse_docs/'
    output_path = base_dir + '/webapp/static/'

    call(("pdftk " + investor_pdf_path + "investor.pdf fill_form %s output " % temp_file_name + output_path + "%s flatten" % out_file_name
          ).split())

    remove_command = "rm %s" % temp_file_name

    kyc_fdf = kyc_fdf_generator(user, investor, nominee, contact, investor_bank, curr_date)

    final_out_file_name = out_file_name
    if len(kyc_fdf) != 0:
        fdf = forge_fdf("", kyc_fdf, [], [], [])
        kyc_temp_file_name = "kyc_temp" + timestamp + ".fdf"
        kyc_out_file_name = "kyc_out" + timestamp + ".pdf"
        final_out_file_name = "final_out" + timestamp + ".pdf"
        fdf_file = open(kyc_temp_file_name, "wb")
        fdf_file.write(fdf)
        fdf_file.close()
        create_kyc = "pdftk " + investor_pdf_path + "kyc.pdf fill_form %s output " % kyc_temp_file_name + output_path + "%s flatten" % kyc_out_file_name
        call((create_kyc).split())
        merge_kyc = "pdftk " + output_path + "%s " % out_file_name + output_path +  "%s cat output " % kyc_out_file_name + output_path + final_out_file_name
        call((merge_kyc).split())
        call(("rm %s" % kyc_temp_file_name).split())

    prefix = "webapp"  # prefix is needed to access the images from media directory.
    # the list of images to be embedded into the pdf follows
    list_of_embeddable_images = []

    # list of individual image type/size (passport/signature) they are based on international standards.
    image_sizes = []

    coords = []  # the lower left bottom corner
    #  co-ordinates for each of the images.

    target_pages = []  # pages of the existing/source pdf into which the images from the images list must be
    #  embedded onto

    images_count_each_page = []  # number of images on each of the target pages.

    nominee_signature = prefix + nominee.nominee_signature.url if nominee.nominee_signature != "" else cons.DEFAULT_IMAGE  # nominee signature image location.
    user_signature = prefix + user.signature.url if user.signature != "" else cons.DEFAULT_IMAGE  # signature_image location.
    list_of_embeddable_images.extend([nominee_signature, user_signature])
    image_sizes.extend([cons.SIGNATURE_SIZE, cons.SIGNATURE_SIZE])
    coords.extend([(390.97, 205.89), (390.97, 23.32)])
    target_pages.extend((0, 0))
    images_count_each_page.extend([2])

    if investor.pan_image:
        list_of_embeddable_images.append(prefix + investor.pan_image.url)
        image_sizes.append(cons.WALLPAPER_SIZE)
        coords.append((10, 150))
        target_pages.append(2)
        images_count_each_page.append(1)

    if investor_bank.bank_cheque_image:
        list_of_embeddable_images.append(prefix + investor_bank.bank_cheque_image.url)
        image_sizes.append(cons.WALLPAPER_SIZE)
        coords.append((10, 150))
        target_pages.append(4)
        images_count_each_page.append(1)

    if contact.front_image:
        list_of_embeddable_images.append(prefix + contact.front_image.url)
        image_sizes.append(cons.SEMI_WALLPAPER_SIZE)
        coords.append((100, 400))
        target_pages.append(5)

    if contact.back_image:
        list_of_embeddable_images.append(prefix + investor.pan_image.url)
        image_sizes.append(cons.SEMI_WALLPAPER_SIZE)
        coords.append((100, 50))
        target_pages.append(5)

    if contact.front_image and contact.back_image:
        images_count_each_page.append(2)
    else:
        images_count_each_page.append(1)
    call(remove_command.split())

    user_identity = prefix + user.identity_info_image.url if user.identity_info_image != "" else cons.DEFAULT_IMAGE  # identity_info image location.
    list_of_embeddable_images.extend([user_identity, user_signature])

    image_sizes.extend([cons.PASSPORT_SIZE, cons.SIGNATURE_SIZE])

    destination_file_name = "destination" + timestamp + ".pdf"

    dest = output_path + destination_file_name  # the final pdf with all images in place.
    exist = output_path + final_out_file_name   # the source pdf without the images.
    coords.extend([(470.14, 620.3), (410.17, 90.03)])

    target_pages.extend((6, 6))

    images_count_each_page.extend([2])

    embed_images(list_of_embeddable_images, image_sizes, coords, target_pages, images_count_each_page, dest, exist)

    return output_path + destination_file_name
