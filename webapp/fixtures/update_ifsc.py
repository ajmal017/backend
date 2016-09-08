from rest_framework import serializers
from profiles.serializers import *
from profiles.models import User
from profiles.models import InvestorBankDetails
from external_api import models as external_models
from django.conf import settings
import os
import csv


def read_csv_and_populate_ifsc_data(csv_file_name):
        
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')
    for row in data_reader:
        if row[0] != 'BANK':
            try:
                bank_detail = external_models.BankDetails.objects.get(ifsc_code=row[1])
                if bank_detail:
                    bank_detail.name = row[0]
                    bank_detail.micr_code = row[2]
                    bank_detail.bank_branch = row[3]
                    bank_detail.address = row[4]
                    bank_detail.phone_number = row[5]
                    bank_detail.city = row[6]
                    bank_detail.district = row[7]
                    bank_detail.state = row[8]
                    bank_detail.updated = True
                    bank_detail.save()
            except external_models.BankDetails.DoesNotExist:
                try:
                    external_models.BankDetails.objects.create(name=row[0], 
                                                           ifsc_code=row[1],
                                                           micr_code=row[2],
                                                           bank_branch=row[3],
                                                           address=row[4],
                                                           phone_number=row[5],
                                                           city=row[6],
                                                           district=row[7],
                                                           state=row[8],
                                                           updated = True
                                                           )
                except Exception as e:
                    print("Error inserting ifsc code: " + row[1] + " error: " + str(e))
            except Exception as e:
                print("Error updating ifsc code: " + row[1] + " error: " + str(e))

IFSC_DATA_FILENAME = 'webapp/fixtures/IFSCCodesMasterList-23 Aug2016.csv'
read_csv_and_populate_ifsc_data(IFSC_DATA_FILENAME)
    