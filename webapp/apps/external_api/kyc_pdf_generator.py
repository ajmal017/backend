from datetime import datetime
from subprocess import call

import os
from fdfgen import forge_fdf

from .utils import embed_images, attach_images
from .kyc_generator import kyc_fdf_generator_new,kyc_fdf_generator
from profiles import models
from .models import Pincode
from . import constants
from webapp.conf import settings
import time


def generate_kyc_pdf(user_id):
    """

    :param user_id: id of user for whom the kyc info is to be generated.
    :return: url of the generated kyc pdf
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    if nominee.nominee_address is None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    pdf_path = base_dir + '/bse_docs/'
    output_path = base_dir + '/webapp/static/'
    kyc_pdf_name = pdf_path + "kyc.pdf"

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    kyc_fdf = kyc_fdf_generator(user, investor, nominee, contact, investor_bank, curr_date)

    if len(kyc_fdf) != 0:
        fdf = forge_fdf("", kyc_fdf, [], [], [])
        kyc_temp_file_name = "kyc_temp" + timestamp + ".fdf"
        kyc_middle_file_name = "kyc_middle" + timestamp + ".pdf"
        fdf_file = open(kyc_temp_file_name, "wb")
        fdf_file.write(fdf)
        fdf_file.close()
        create_kyc = "pdftk " + kyc_pdf_name + " fill_form %s output " % kyc_temp_file_name + output_path + \
                     "%s flatten" % kyc_middle_file_name
        call(create_kyc.split())

        call((("rm %s") % kyc_temp_file_name).split())

    prefix = ""  # prefix is needed to access the images from media directory.
    # the list of images to be embedded into the pdf follows
    list_of_embeddable_images = []

    # list of individual image type/size (passport/signature) they are based on international standards.
    image_sizes = []

    coords = []  # the lower left bottom corner
    #  co-ordinates for each of the images.

    target_pages = []  # pages of the existing/source pdf into which the images from the images list must be
    #  embedded onto

    images_count_each_page = []  # number of images on each of the target pages.

    user_identity = prefix + user.identity_info_image.url if user.identity_info_image != "" else constants.DEFAULT_IMAGE  # identity_info image location.
    user_signature = prefix + user.signature.url if user.signature != "" else constants.DEFAULT_IMAGE  # signature_image location.
    list_of_embeddable_images.extend([user_identity, user_signature])
    image_sizes.extend([constants.PASSPORT_SIZE, constants.SIGNATURE_SIZE])
    coords.extend([(470.14, 620.3), (410.17, 90.03)])
    target_pages.extend((0, 0))
    images_count_each_page.extend([2])

    # file initializations.
    kyc_middle_file_name = "kyc_middle" + timestamp + ".pdf"
    exist = output_path + kyc_middle_file_name  # the source pdf without the images.
    kyc_destination_file_name = "kyc_destination" + timestamp + ".pdf"
    output_file = output_path + kyc_destination_file_name  # final_output of the completed kyc_pdf.

    if kyc_pdf_name.endswith("kyc.pdf"):
        # additional pan card and address_proof embeds.
        if investor.pan_image:
            list_of_embeddable_images.append(prefix + investor.pan_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 270))
            target_pages.append(2)
            images_count_each_page.append(1)

        if contact.front_image:
            list_of_embeddable_images.append(prefix + contact.front_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 400))
            target_pages.append(3)

        if contact.back_image:
            list_of_embeddable_images.append(prefix + contact.back_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 50))
            target_pages.append(3)

        if contact.front_image and contact.back_image:
            images_count_each_page.append(2)
        else:
            images_count_each_page.append(1)

        # finally_embed the images.
        embed_images(list_of_embeddable_images, image_sizes, coords, target_pages, images_count_each_page, output_file, exist)

    else:
        # if not embed mode,  then attach pan and contact images at the end.
        attachable_images = []
        investor_image = prefix + investor.pan_image.url if investor.pan_image != "" else None
        contact_front = prefix + contact.front_image.url if contact.front_image != "" else None
        contact_back = prefix + contact.back_image.url if contact.back_image != "" else None
        attachable_images.extend((investor_image, contact_front, contact_back))
        # finally append the images to the end of the generated pdf.
        attach_images(attachable_images, exist, output_file)

    return output_file






def generate_kyc_pdf_new(user_id):
    """

    :param user_id: id of user for whom the kyc info is to be generated.
    :return: url of the generated kyc pdf
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    if nominee.nominee_address is None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    pdf_path = base_dir + '/bse_docs/'
    output_path = base_dir + '/webapp/static/'
    kyc_pdf_name = pdf_path + "kyc_new.pdf"

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    kyc_fdf = kyc_fdf_generator_new(user, investor, nominee, contact, investor_bank, curr_date)

    if len(kyc_fdf) != 0:
        fdf = forge_fdf("", kyc_fdf, [], [], [])
        kyc_temp_file_name = "kyc_temp" + timestamp + ".fdf"
        kyc_middle_file_name = "kyc_middle" + timestamp + ".pdf"
        fdf_file = open(kyc_temp_file_name, "wb")
        fdf_file.write(fdf)
        fdf_file.close()
        create_kyc = "pdftk " + kyc_pdf_name + " fill_form %s output " % kyc_temp_file_name + output_path + \
                     "%s flatten" % kyc_middle_file_name
        call(create_kyc.split())

        call((("rm %s") % kyc_temp_file_name).split())

    prefix = ""  # prefix is needed to access the images from media directory.
    # the list of images to be embedded into the pdf follows
    list_of_embeddable_images = []

    # list of individual image type/size (passport/signature) they are based on international standards.
    image_sizes = []

    coords = []  # the lower left bottom corner
    #  co-ordinates for each of the images.

    target_pages = []  # pages of the existing/source pdf into which the images from the images list must be
    #  embedded onto

    images_count_each_page = []  # number of images on each of the target pages.

    user_identity = prefix + user.identity_info_image.url if user.identity_info_image != "" else constants.DEFAULT_IMAGE  # identity_info image location.
    user_signature = prefix + user.signature.url if user.signature != "" else constants.DEFAULT_IMAGE  # signature_image location.
    list_of_embeddable_images.append(user_identity)
    image_sizes.append(constants.PASSPORT_SIZE)
    coords.append((510, 490))
    target_pages.append(0)
    images_count_each_page.append(1)
    
    list_of_embeddable_images.append(user_signature)
    image_sizes.append(constants.SIGNATURE_SIZE)
    coords.append((450, 235))
    target_pages.append(1)
    images_count_each_page.append(1)
    
    # file initializations.
    kyc_middle_file_name = "kyc_middle" + timestamp + ".pdf"
    exist = output_path + kyc_middle_file_name  # the source pdf without the images.
    kyc_destination_file_name = "kyc_destination" + timestamp + ".pdf"
    output_file = output_path + kyc_destination_file_name  # final_output of the completed kyc_pdf.

    if kyc_pdf_name.endswith("kyc_new.pdf"):
        # finally_embed the images.
        if investor.pan_image:
            list_of_embeddable_images.append(prefix + investor.pan_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 270))
            target_pages.append(4) # change to 4
            images_count_each_page.append(1)

        if contact.front_image:
            list_of_embeddable_images.append(prefix + contact.front_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 400))
            target_pages.append(5) #change to 5

        if contact.back_image:
            list_of_embeddable_images.append(prefix + contact.back_image.url)
            image_sizes.append(constants.FIT_SIZE)
            coords.append((100, 50))
            target_pages.append(5) #change to 5

        if contact.front_image and contact.back_image:
            images_count_each_page.append(2)
        else:
            images_count_each_page.append(1)
        
        # permanent are not same
        if not contact.address_are_equal:
            if contact.permanent_front_image:
                list_of_embeddable_images.append(prefix + contact.permanent_front_image.url)
                image_sizes.append(constants.FIT_SIZE)
                coords.append((100, 400))
                target_pages.append(6) #change to 6
                 
            
            if contact.permanent_back_image:
                list_of_embeddable_images.append(prefix + contact.permanent_back_image.url)
                image_sizes.append(constants.FIT_SIZE)
                coords.append((100, 50))
                target_pages.append(6) #change to 6
        
            if contact.permanent_front_image and contact.permanent_back_image:
                images_count_each_page.append(2)
            elif contact.permanent_front_image and not contact.permanent_back_image:
                images_count_each_page.append(1)         
             
            
        embed_images(list_of_embeddable_images, image_sizes, coords, target_pages, images_count_each_page, output_file, exist)

    else:
        # if not embed mode,  then attach pan and contact images at the end.
        attachable_images = []
        investor_image = prefix + investor.pan_image.url if investor.pan_image != "" else None
        contact_front = prefix + contact.front_image.url if contact.front_image != "" else None
        contact_back = prefix + contact.back_image.url if contact.back_image != "" else None
        attachable_images.extend((investor_image, contact_front, contact_back))
        # finally append the images to the end of the generated pdf.
        attach_images(attachable_images, exist, output_file)

    return output_file

