from rest_framework import serializers
from profiles.serializers import *
from profiles.models import User
from profiles.models import InvestorInfo
from profiles.models import InvestorBankDetails
from profiles.models import NomineeInfo
from profiles.models import ContactInfo
from core.models import Fund
from django.conf import settings
from django.core.files import File
import os

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
AWS_STORAGE_BUCKET_NAME='user-files.finaskus.com'
AWS_ACCESS_KEY_ID='AKIAI5CZ5X3YRZTATSZA'
AWS_SECRET_ACCESS_KEY='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'
MEDIA_URL = 'http://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME

def openSourceFile(currentPath):
    try:
        print(currentPath)
        im = open(currentPath, 'rb')
        imFile = File(im)
        imFile.name = os.path.basename(currentPath)
        return imFile
    except Exception as e:
        print("Error opening file: " + str(e))
    return None

def migrateAll():
    users = User.objects.all()
    for u in users:
        print("Links changed for user: " + u.email)
        try:
            investor = InvestorInfo.objects.get(user=u)
            if investor and investor.pan_image:
                print(u.email + "," + str(investor.pan_image))
                currentPath = settings.MEDIA_ROOT + '/' + str(investor.pan_image)
                imFile = openSourceFile(currentPath)
                if imFile:
                    investor.pan_image = imFile
                    investor.save()
                    print("Investor pan image url: " + investor.pan_image.url)
                    imFile.close()
                else:
                    print("Could not open source pan image file for : " + u.email)
        except InvestorInfo.DoesNotExist:
            print('Investor Info does not exist Exception for user: ' + u.email)
        except Exception as e:
            print('Investor Info Exception for user: ' + u.email + ' : ' + str(e))
        try:
            identity_imFile = profile_imFile = sign_imFile = videothumb_imFile = video_imFile = None
            if u.identity_info_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(u.identity_info_image)
                print(u.email + "," + str(u.identity_info_image))
                identity_imFile = openSourceFile(currentPath)
                if identity_imFile:
                    u.identity_info_image = identity_imFile
                else:
                    print("Could not open source identity image file for : " + u.email)
            if u.image:
                currentPath = settings.MEDIA_ROOT + '/' + str(u.image)
                print(u.email + "," + str(u.image))
                profile_imFile = openSourceFile(currentPath)
                if profile_imFile:
                    u.image = profile_imFile
                else:
                    print("Could not open source profile image file for : " + u.email)
            if u.signature:
                currentPath = settings.MEDIA_ROOT + '/' + str(u.signature)
                print(u.email + "," + str(u.signature))
                sign_imFile = openSourceFile(currentPath)
                if sign_imFile:
                    u.signature = sign_imFile
                else:
                    print("Could not open source signature image file for : " + u.email)
            if u.user_video_thumbnail:
                currentPath = settings.MEDIA_ROOT + '/' + str(u.user_video_thumbnail)
                print(u.email + "," + str(u.user_video_thumbnail))
                videothumb_imFile = openSourceFile(currentPath)
                if videothumb_imFile:
                    u.user_video_thumbnail = videothumb_imFile
                else:
                    print("Could not open video thumbnail image file for : " + u.email)
            if u.user_video:
                currentPath = settings.MEDIA_ROOT + '/' + str(u.user_video)
                print(u.email + "," + str(u.user_video))
                video_imFile = openSourceFile(currentPath)
                if video_imFile:
                    u.user_video = video_imFile
                else:
                    print("Could not open video file for : " + u.email)
            u.save()
            if identity_imFile:
                identity_imFile.close()
            if profile_imFile:
                profile_imFile.close()
            if sign_imFile:
                sign_imFile.close()
            if videothumb_imFile:
                videothumb_imFile.close()
            if video_imFile:
                video_imFile.close()
            if u.identity_info_image:
                print(u.identity_info_image.url)
            if u.image:
                print(u.image.url)
            if u.signature:
                print(u.signature.url)
            if u.user_video_thumbnail:
                print(u.user_video_thumbnail.url)
            if u.user_video:
                print(u.user_video.url)
        except Exception as e:
            print('Exception for user: ' + u.email + ' : ' + str(e))
        try:
            investor_bank_details = InvestorBankDetails.objects.get(user=u)
            if investor_bank_details and investor_bank_details.bank_cheque_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(investor_bank_details.bank_cheque_image)
                print(u.email + "," + str(investor_bank_details.bank_cheque_image))
                imFile = openSourceFile(currentPath)
                if imFile:
                    investor_bank_details.bank_cheque_image = imFile
                    investor_bank_details.save()
                    print("Bank cheque image url: " + investor_bank_details.bank_cheque_image.url)
                    imFile.close()
                else:
                    print("Could not open source cheque image file for : " + u.email)
        except InvestorBankDetails.DoesNotExist:
            print('Bank Info does not exist Exception for user: ' + u.email)
        except Exception as e:
            print('Bank Info Exception for user: ' + u.email + ' : ' + str(e))
        try:
            nominee = NomineeInfo.objects.get(user=u)
            if nominee and nominee.nominee_signature:
                currentPath = settings.MEDIA_ROOT + '/' + str(nominee.nominee_signature)
                print(u.email + "," + str(nominee.nominee_signature))
                imFile = openSourceFile(currentPath)
                if imFile:
                    nominee.nominee_signature = imFile
                    nominee.save()
                    print("Nominee SIgnature image url: " + nominee.nominee_signature.url)
                    imFile.close()
                else:
                    print("Could not open source nominee signature image file for : " + u.email)
        except NomineeInfo.DoesNotExist:
            print('nominee Info does not exist Exception for user: ' + u.email)
        except Exception as e:
            print('Nominee Info Exception for user: ' + u.email + ' : ' + str(e))
        try:
            contact = ContactInfo.objects.get(user=u)
            front_imFile = back_imFile = perm_front_imFile = perm_back_imFile = None
            if contact and contact.front_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(contact.front_image)
                print(u.email + "," + str(contact.front_image))
                front_imFile = openSourceFile(currentPath)
                if front_imFile:
                    contact.front_image = front_imFile
                else:
                    print("Could not open source Contact Front image file for : " + u.email)
            if contact and contact.back_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(contact.back_image)
                print(u.email + "," + str(contact.back_image))
                back_imFile = openSourceFile(currentPath)
                if back_imFile:
                    contact.back_image = back_imFile
                else:
                    print("Could not open source Contact Back image file for : " + u.email)
            if contact and contact.permanent_front_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(contact.permanent_front_image)
                print(u.email + "," + str(contact.permanent_front_image))
                perm_front_imFile = openSourceFile(currentPath)
                if perm_front_imFile:
                    contact.permanent_front_image = perm_front_imFile
                else:
                    print("Could not open source Contact Permanent Front image file for : " + u.email)
            if contact and contact.permanent_back_image:
                currentPath = settings.MEDIA_ROOT + '/' + str(contact.permanent_back_image)
                print(u.email + "," + str(contact.permanent_back_image))
                perm_back_imFile = openSourceFile(currentPath)
                if perm_back_imFile:
                    contact.permanent_back_image = perm_back_imFile
                else:
                    print("Could not open source Contact Permanent Back image file for : " + u.email)
            if contact:
                contact.save()
                if front_imFile:
                    front_imFile.close()
                if back_imFile:
                    back_imFile.close()
                if perm_front_imFile:
                    perm_front_imFile.close()
                if perm_back_imFile:
                    perm_back_imFile.close()
                if contact.front_image:
                    print("Contact Front image url: " + contact.front_image.url)
                if contact.back_image:
                    print("Contact Back image url: " + contact.back_image.url)
                if contact.permanent_front_image:
                    print("Contact Permanent Front image url: " + contact.permanent_front_image.url)
                if contact.permanent_back_image:
                    print("Contact Permanent Back image url: " + contact.permanent_back_image.url)
                    
        except ContactInfo.DoesNotExist:
            print('Contact Info does not exist Exception for user: ' + u.email)
        except Exception as e:
            print('Contact Info Exception for user: ' + u.email + ' : ' + str(e))
    funds = Fund.objects.all()
    for fund in funds:
        try:
            if fund.image_url:
                currentPath = settings.MEDIA_ROOT + '/' + str(fund.image_url)
                print(str(fund.id) + "," + str(fund.image_url))
                imFile = openSourceFile(currentPath)
                if imFile:
                    fund.image_url = imFile
                    fund.save()
                    print("Fund image url: " + fund.image_url)
                    imFile.close()
                else:
                    print("Could not open source fund image file for : " + fund.id)
        except Exception as e:
            print('Fund Exception for id: ' + fund.id + ' : ' + str(e))
migrateAll()
