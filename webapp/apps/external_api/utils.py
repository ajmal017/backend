from . import constants, serializers
from webapp.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image

import requests

import csv
import logging
import ghostscript
from subprocess import call
from io import BytesIO
import time


def read_csv_and_populate_pin_code_model():
    """
    A utility to read a csv file and populate its data into pin code table
    :return:
    """
    csv_file_name = constants.CSV_FILE_NAME  # name of the csv file
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')  # open the csv file

    # for each row except the header row populate data in table pin code
    logger = logging.getLogger('django.error')
    entries = set()
    for row in data_reader:
        if row[0] != constants.PIN_CODE:
            # assuming first row in csv file is pin code, second is city and third state
            key = (row[0], row[1], row[2])
            if key not in entries:
                data = {constants.PIN_CODE: row[0], constants.STATE: row[2], constants.CITY: row[1]}
                serializer = serializers.PinCodeSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    logger.error(data[constants.PIN_CODE] + ' ' + data[constants.STATE] + ' ' + data[constants.CITY])
                entries.add(key)


def generate_url_for_historical_data(mstar_id, start_date, end_date):
    """
    generates a url for historical data
    :param mstar_id: the mstar id of fund for which url is to be constructed
    :param start_date: the start date from which we need historical data
    :param end_date: the end date till which we need historical data
    :return:
    """
    return constants.HISTORICAL_DATA_API + mstar_id + constants.ACCESS_CODE + settings.MORNING_STAR_ACCESS_CODE + \
           constants.START_DATE + str(start_date) + constants.END_DATE + str(end_date) + constants.FREQUENCY


def generate_url_for_category_history(category_id, start_date, end_date):
    """
    generates a url for category historical data
    :param category_id:the id of category
    :param start_date: the date from which we want data
    :param end_date:the date till which we want data
    :return:
    """
    return constants.HISTORICAL_NAV_CATEGORY_API + settings.MORNING_STAR_ACCESS_CODE + constants.CATEGORY_ID + \
           category_id + constants.UNIVERSE + constants.START_DATE + str(start_date) + constants.END_DATE + \
           str(end_date) + constants.REGION


def read_csv_and_populate_bank_details():
    """
    A utility to read a csv file and populate its data into bank details model
    :return:
    """
    csv_file_name = constants.CSV_BANK_FILE_PATH  # name of the csv file
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')  # open the csv file

    # for each row except the header row populate data in table bank details
    logger = logging.getLogger('django.error')
    for row in data_reader:
        if row[0] != constants.IFSC:
            # assuming first column in csv file is ifsc code, second is bank name, third is branch, fourth is address
            # fifth is contact, sixth is city, seventh is district and eighth is state
            data= {constants.IFSC_CODE: row[0], constants.BANK_NAME: row[1], constants.BRANCH: row[2],
                   constants.ADDRESS: row[3], constants.CONTACT: row[4], constants.CITY: row[5],
                   constants.DISTRICT: row[6], constants.STATE: row[7]}
            serializer = serializers.BankDetailsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                logger.error(data[constants.IFSC_CODE])


def generate_tiff(pdf_name, bank_cheque_image):
    """
    This function accepts the data and image filled bse pdf and converts it into tiff and concatenates bank cheque tiff,
    if bank cheque leaf exists.
    :param pdf_name: data and image filled bse pdf to be converted to .tiff format
    :param bank_cheque_image: bank cheque image to be converted into tiff and joined with the pdf tiff.
    :return: The file path of the generated tiff file.
    """

    # initial setup
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    tiff_output_path = "webapp/static/"
    out_tiff_file = "out" + timestamp + ".tiff"  # the final tiff file.
    prefix_out_tiff_file = tiff_output_path + out_tiff_file
    uncompressed_combined_tiff_file = tiff_output_path + "combined" + timestamp + ".tiff"
    out_pdf_tiff_file = tiff_output_path + "pdfTIFF" + timestamp + ".tiff"
    out_image_png_file = tiff_output_path + "imagePNG_" + timestamp + ".png"
    out_image_pdf_file = tiff_output_path + "imagePDF_" + timestamp + ".pdf"
    out_image_tiff_file = tiff_output_path + "imageTIFF_" + timestamp + ".tiff"

    # business logic
    args = [b'gs', b'-q', b'-dNOPAUSE', b'-sDEVICE=tiffg4', b'-sOutputFile=' + bytes(out_pdf_tiff_file, 'utf-8'),
            bytes(pdf_name, 'utf-8'), b'-c', b'quit']  # this converts page1pdf to tiff with gray-scale g4 as device.
    ghostscript.Ghostscript(*args)

    if bank_cheque_image:
        response = requests.get(bank_cheque_image.url)
        actual_image = Image.open(BytesIO(response.content))
        original_size = actual_image.size  # actual image dimensions (width, height)
        size = constants.TIFF_LANDSCAPE_SIZE  # assume by default landscape.
        if original_size[0] < original_size[1]:
            # the original image is portrait.
            size = constants.TIFF_PORTRAIT_SIZE
            if settings.ROTATE_IMAGE:
                # settings set to mandatory rotate the portrait image to landscape image.
                actual_image = actual_image.rotate(90)
                size = constants.TIFF_LANDSCAPE_SIZE

        # aspect ratio maintenance logic.
        image_w, image_h = actual_image.size
        if (size == constants.TIFF_LANDSCAPE_SIZE and (image_w > 1920 or image_w < 840)) or \
            (size == constants.TIFF_PORTRAIT_SIZE and (image_h > 1920 or image_h < 840)):
            aspect_ratio = image_w / float(image_h)
            new_height = int(size[0] / aspect_ratio)
            # note it is width X height always, in real life too not just python.
            # portrait is 800 x 1,200 these are minimum dimensions.
            # landscape is 1,024 x 512 these are minimum dimensions.
            if new_height < 1200:
                size = constants.TIFF_LANDSCAPE_SIZE
            else:
                # the given image is portrait
                size = constants.TIFF_PORTRAIT_SIZE
            resized_image = actual_image.resize(size, Image.ANTIALIAS)
        else:
            resized_image = actual_image
        """
        temp_image_outfile = open(out_image_png_file, 'wb')
        resized_image.save(temp_image_outfile, "PNG", optimize=True)
        temp_image_outfile.close()
        resized_image = Image.open(out_image_png_file)
        """
        outfile = open(out_image_pdf_file, 'wb')
        # save the image as pdf for input to ghostscript
        resized_image.save(outfile, "PDF", resolution=100.0)
        outfile.close()
        actual_image.close()
        resized_image.close()
        args = [b'gs', b'-q', b'-dNOPAUSE', b'-sDEVICE=tiff32nc', b'-sOutputFile=' + bytes(out_image_tiff_file, 'utf-8'),
                bytes(out_image_pdf_file, 'utf-8'), b'-c', b'quit']  # this converts img to tiff with colored-scaling.
        ghostscript.Ghostscript(*args)
        # concatenates the 2 tiff files. pdf-tiff + img-tiff
        call(("tiffcp " + out_pdf_tiff_file + " " + out_image_tiff_file + " " + uncompressed_combined_tiff_file).split())
        # removes all temporary files.
        call(("rm " + out_image_pdf_file + " " + out_image_tiff_file + " " + out_pdf_tiff_file).split())
    else:
        uncompressed_combined_tiff_file = out_pdf_tiff_file

    # LZW compression to reduce download size of the tiff.
    call(("convert " + uncompressed_combined_tiff_file + " -compress LZW " + prefix_out_tiff_file).split())
    return out_tiff_file


def embed_images(images_list, sizes, coords, target_pages, images_count_each_page, destination, existing):
    """

    :param images_list: the list of image urls , these are the images to be embedded into the existing/source pdf
    :param sizes: list of signature sizes for each of the images
    :param coords: the list of tuples for the co-ordinates of each of the images
    :param target_pages: tuple of pages of the existing/source pdf into which the images must be embedded
    :param images_count_each_page: number of images on each of the target pages.
    :param destination: the final generated pdf with all the images in it.
    :param existing: the source pdf to extract the data from.
    :return: None
    """
    def generate_img_canvas(the_image, size, coord_block):
        """

        :param size: One of several standard types of sizes as mentioned in the constants file.
        :param the_image: Individual image that is converted into a canvas element
        :param coord_block: The co-ordinates for the pertinent image.
        Co-ordinates must be (x,y) of the lower left corner of the area in which the image should be inserted
        :return: the generated image canvas
        """
        img_temp = BytesIO()
        response = requests.get(the_image)
        actual_image = Image.open(BytesIO(response.content))
        width = constants.SEMI_WALLPAPER_WIDTH * cm
        height = constants.SEMI_WALLPAPER_HEIGHT * cm

        if size == constants.PASSPORT_SIZE or size == constants.SIGNATURE_SIZE:
            width = constants.WIDTH*cm
            height = constants.HEIGHT*cm
            resized_image = actual_image.resize(size, Image.ANTIALIAS)
        elif size == constants.TIFF_SIGNATURE_SIZE:
            width = constants.WIDTH*cm
            height = constants.TIFF_HEIGHT*cm
            resized_image = actual_image.resize(size, Image.ANTIALIAS)
        elif size == constants.ORIGINAL_SIZE:
            resized_image = actual_image.resize(actual_image.size, Image.ANTIALIAS)
            width = (constants.ORIGINAL_WIDTH*resized_image.width)*cm
            height = (constants.ORIGINAL_HEIGHT*resized_image.height)*cm
        else:
            # in case of size==constants.FIT_SIZE
            original_size = actual_image.size  # actual image dimensions (width, height)
            size = constants.LANDSCAPE_SIZE  # assume by default landscape.
            if original_size[1] >= 1200:
                # the original image is portrait.
                size = constants.PORTRAIT_SIZE
                if settings.ROTATE_IMAGE:
                    # settings set to mandatory rotate the portrait image to landscape image.
                    actual_image = actual_image.rotate(90)
                    size = constants.LANDSCAPE_SIZE
            
            # aspect ratio maintenance logic.
            image_w, image_h = actual_image.size
            aspect_ratio = image_w / float(image_h)
            new_height = int(size[0] / aspect_ratio)
            # note it is width X height always, in real life too not just python.
            # portrait is 800 x 1,200 these are minimum dimensions.
            # landscape is 1,024 x 512 these are minimum dimensions.
            if new_height < 1200:
                # the given image is landscape
                final_width = size[0]
                final_height = new_height
            else:
                # the given image is portrait
                final_width = int(aspect_ratio * size[1])
                final_height = size[1]

            resized_image = actual_image.resize((final_width, final_height), Image.ANTIALIAS)
        
        img_reader = ImageReader(resized_image)
        can = canvas.Canvas(img_temp)
        can.drawImage(img_reader, coord_block[0], coord_block[1], preserveAspectRatio=True, width=width, height=height, mask='auto')
        can.save()
        img_temp.seek(0)
        return img_temp

    def generate_output(canvas_list, existing, pages):
        """

        :param canvas_list: The list of canvases of the images
        :param existing: the existing/source pdf
        :param pages: the list of target page nos. onto which the images are embedded.
        :return: the PdfWriter's output object with all correctly generated pages with images embedded.
        """

        existing_pdf = PdfFileReader(open(existing, "rb"))
        pdf_list = []  # list of PdfReader objects for each of the images.
        for i in canvas_list:
            pdf_list.append(PdfFileReader(i))
        output = PdfFileWriter()  # the PdfWriter's output object
        existing_num_pages = existing_pdf.getNumPages()  # returns the number of pages in the source pdf.
        existing_pages = [existing_pdf.getPage(i) for i in range(existing_num_pages)]  # extract all the pages from
        # the source pdf

        pages_set = set(pages)  # removes duplicates in target pages. This is used only for extracting correct no.
        # of target pages

        target_pages = [existing_pages[i] for i in pages_set]  # the target pages are extracted.
        for i in range(len(target_pages)):
            for j in range(images_count_each_page.pop(0)):
                target_pages[i].mergePage(pdf_list.pop(0).getPage(0))  # merge image pdfs at correct postion in the
                # target page.

        for i in range(existing_num_pages):
            if i not in pages:
                output.addPage(existing_pages[i])  # write existing page if unmodified.
            else:
                output.addPage(target_pages.pop(0))  # else write image embedded page.
        return output

    img_canvas_list = []  # list for canvases of each of the images

    for i in range(len(images_list)):
        img_canvas_list.append(generate_img_canvas(images_list[i], sizes[i], coords[i]))

    output = generate_output(img_canvas_list, existing, target_pages)

    # finally, write "output" to a real output file

    output_stream = open(destination, "wb")
    output.write(output_stream)
    output_stream.close()
    return None


def attach_images(images_list, source_pdf, output_location):
    """
    This appends the required images to the completely filled kyc form
    :param output_location: location of the final output file, where the output has to be redirected.
    :param source_pdf: the data filled kyc file, which requires the image appending.
    :param images_list: the array of images that need to be attached at the end.
    :return: None. The output file location is present already with the callee.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    string_of_attachable_pdf = ""
    count = 0
    for image in images_list:
        if image:
            response = requests.get(image)
            actual_image = Image.open(BytesIO(response.content))
            # in case of size==constants.FIT_SIZE
            original_size = actual_image.size  # actual image dimensions (width, height)
            size = constants.LANDSCAPE_SIZE  # assume by default landscape.
            if original_size[1] >= 1200:
                # the original image is portrait.
                size = constants.PORTRAIT_SIZE
                if settings.ROTATE_IMAGE:
                    # settings set to mandatory rotate the portrait image to landscape image.
                    actual_image.rotate(90)
                    size = constants.LANDSCAPE_SIZE

            # aspect ratio maintenance logic.
            image_w, image_h = actual_image.size
            aspect_ratio = image_w / float(image_h)
            new_height = int(size[0] / aspect_ratio)
            # note it is width X height always, in real life too not just python.
            # portrait is 800 x 1,200 these are minimum dimensions.
            # landscape is 1,024 x 512 these are minimum dimensions.
            if new_height < 1200:
                # the given image is landscape
                final_width = size[0]
                final_height = new_height
            else:
                # the given image is portrait
                final_width = int(aspect_ratio * size[1])
                final_height = size[1]

            resized_image = actual_image.resize((final_width, final_height), Image.ANTIALIAS)
            temp_file_name = str(count) + timestamp + ".pdf"
            outfile = open(temp_file_name, 'wb')
            resized_image.save(outfile, "PDF")  # converts image to pdf
            outfile.close()
            string_of_attachable_pdf = string_of_attachable_pdf+" "+temp_file_name
            resized_image.close()
            count += 1

    # command constructed to append the image pdfs with data filled kyc_pdf
    cmd = "pdftk "+source_pdf+string_of_attachable_pdf+" "+"cat output "+output_location
    call(cmd.split())

    # removes all temporarily generated files.
    rm_cmd = "rm"+string_of_attachable_pdf
    call(rm_cmd.split())
    return None
