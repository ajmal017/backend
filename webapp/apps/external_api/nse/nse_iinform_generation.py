from fdfgen import forge_fdf

from external_api.utils import generate_tiff, embed_images
from profiles import models
from external_api.models import Pincode
from external_api import constants

import os
from datetime import datetime
from subprocess import call
import time


def nse_investor_info_generator(user_id):
    """

    :param user_id: id of user for whom the bse investor info is to be generated
    :return:
    """
    user=models.User.objects.get(id=user_id)
    investor=models.InvestorInfo.objects.get(user=user)
    nominee=models.NomineeInfo.objects.get(user=user)
    contact=models.ContactInfo.objects.get(user=user)
    investor_bank=models.InvestorBankDetails.objects.get(user=user)
    curr_date=datetime.now()

    nominee_address = nominee.nominee_address
    if nominee.nominee_address == None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address


    investor_dict={
     "ACNo" : investor_bank.account_number,
     "AcType" : investor_bank.account_type,
     "BankAddress" : investor_bank.ifsc_code.address,
     "BankCity" : investor_bank.ifsc_code.city,
     "BankCountry" : constants.INDIA,
     "BankPincode" : None,
     "Branch" : investor_bank.ifsc_code.bank_branch,
     "City" : contact.communication_address.pincode.city,
     "ContactAddress" : contact.communication_address.address_line_1,
     "Country" : constants.INDIA,
     "DateofBirth" : investor.dob.strftime('%d-%m-%Y'),
     "DpId" : None,
     "Email" : contact.email,
     "FatherName" : investor.father_name,
     "FaxOff" : None,
     "FaxRes" : None,
     "GuardianNameIfNomineeMinor" : nominee.guardian_name if nominee else None,
     "GuardianPAN" : None,
     "IFSCCode" : investor_bank.ifsc_code.ifsc_code,
     "Mobile" : contact.phone_number,
     "ModeofHolding" : None,  # TODO
     "MotherName" : None,  # TODO
     "NameofThirdApplicant" : None,
     "NameFirstApplicant" : investor.applicant_name,
     "NameGuardian" : nominee.guardian_name if nominee else None,
     "NameofBank" : investor_bank.ifsc_code.name,
     "NameofSecondApplicant" : None,
     "NomineeAddress" : nominee.nominee_address.address_line_1,
     "NomineeCity" : nominee.nominee_address.pincode.city,
     "NomineeName" : nominee.nominee_name if nominee else None,
     "NomineePincode" : nominee.nominee_address.pincode.pincode,
     "NomineeRelationship" : nominee.get_relationship_with_investor_display() if nominee else None,
     "NomineeState" : nominee.nominee_address.pincode.state,
     "OverseasAddress" : None,
     "OverseasCity" : None,
     "OverseasCountry" : None,
     "OverseasPincode" : None,
     "PANNumber" : investor.pan_number,
     "PANNumber_2" : None,
     "PANNumber_3" : None,
     "Pincode" : contact.communication_address.pincode.pincode,
     "SignatureDate" : curr_date.strftime('%d-%m-%Y'),
     "SignaturePlace" : contact.communication_address.pincode.city,
     "State" : contact.communication_address.pincode.state,
     "TaxStatus" : None,  # TODO
     "TelOff" : None,
     "TelRes": None
     }

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

    temp_file_name = "temp" + timestamp + ".fdf"
    out_file_name = "out" + timestamp + ".pdf"

    fields = [(key, value) for key, value in investor_dict.items()]
    fdf = forge_fdf("", fields, [], [], [])
    fdf_file = open(temp_file_name, "wb")
    fdf_file.write(fdf)
    fdf_file.close()

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    bse_investor_pdf_path = base_dir + '/nse_docs/'
    output_path = base_dir + '/webapp/static/'
    iin_file_name = bse_investor_pdf_path + "iin.pdf"

    call(("pdftk " + iin_file_name + " fill_form %s output " % temp_file_name + output_path + "%s flatten"
          % out_file_name).split())
    # remove the temporary generated fdf file.
    call(("rm " + temp_file_name).split())
    prefix = "webapp"  # prefix is needed to access the images from media directory.

    # the list of images to be embedded into the pdf follows
    user_signature = prefix + user.signature.url if user.signature != "" else constants.DEFAULT_IMAGE  # signature_image location.
    list_of_embeddable_images = [user_signature, ]

    # list of individual image type/size (passport/signature) they are based on international standards.
    image_sizes = [constants.TIFF_SIGNATURE_SIZE, ]

    iin_destination_file_name = "iin_destination" + timestamp + ".pdf"

    dest = output_path + iin_destination_file_name  # the final pdf with all images in place.
    exist = output_path + out_file_name   # the source pdf without the images.
    coords = [(125, 24), ]  # the lower left bottom corner
    #  co-ordinates for each of the images.

    target_pages = (0, )  # pages of the existing/source pdf into which the images from the images list must be
    #  embedded onto

    images_count_each_page = [1, ]  # number of images on each of the target pages.

    # following makes a call to the embed images function in the utils
    embed_images(list_of_embeddable_images, image_sizes, coords, target_pages, images_count_each_page, dest, exist)
    # following generates the tiff file.

    final_tiff_file_name = generate_tiff(output_path + iin_destination_file_name, investor_bank.bank_cheque_image)
    return output_path + final_tiff_file_name
