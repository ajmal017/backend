

def full_name_split(full_name):
    
    first_name,middle_name,last_name = None,None,None
    try:
        name = full_name.split()
        if len(name) > 0:
            first_name = name[0]
        
        if len(name) > 1:
            last_name = name[-1]
        
        if len(name) > 2:
            i=1
            middle_name = ""
            while i <= len(name)-2: 
                middle_name += " " + name[i]
                i += 1
    except:
        first_name,middle_name,last_name = None,None,None
    return first_name,middle_name,last_name

def kyc_fdf_generator(user, investor, nominee, contact, investor_bank, curr_date):


    permanent_address = {
        'pincode': {'city': None, 'state': None, 'pincode': None},
        'address_line_1': None,
        'address_line_2': None
    }

    if contact.permanent_address is not None:
        permanent_address = contact.permanent_address

    kyc_dict = {
        'AadharNumber': None,
        'Birth-dd': investor.dob.strftime("%d"),
        'Birth-mm': investor.dob.strftime("%m"),
        'Birth-yyyy': investor.dob.strftime("%Y"),
        'CorrespAddressProof-BankStatement': True if contact.address_proof_type == 5 else False,
        'CorrespAddressProof-DriversLicense': True if contact.address_proof_type == 2 else False,
        'CorrespAddressProof-ElectricityBill': True if contact.address_proof_type == 6 else False,
        'CorrespAddressProof-GasBill': True if contact.address_proof_type == 6 else False,
        'CorrespAddressProof-LeaseAgreement': False,  # TODO ask if we need to increse address proof types
        'CorrespAddressProof-Other': False,
        'CorrespAddressProof-Other-Specify': None,
        'CorrespAddressProof-Passport': True if contact.address_proof_type == 1 else False,
        'CorrespAddressProof-RationCard': True if contact.address_proof_type == 7 else False,
        'CorrespAddressProof-TelBill': True if contact.address_proof_type == 6 else False,
        'CorrespAddressProof-VoterID': True if contact.address_proof_type == 3 else False,
        'CorrespondenceAddress-City': contact.communication_address.pincode.city,
        'CorrespondenceAddress-Country': "INDIA",
        'CorrespondenceAddress-Pincode': contact.communication_address.pincode.pincode,
        'CorrespondenceAddress-State': contact.communication_address.pincode.state,
        'CorrespondenceAddress1': contact.communication_address.address_line_1,
        'CorrespondenceAddress2': contact.communication_address.address_line_2,
        'CorrespondenceAddress3': None,
        'CorrespondenceAddressProof-dd': None,
        'CorrespondenceAddressProof-mm': None,
        'CorrespondenceAddressProof-yyyy': None,
        'EmailID': contact.email,
        'Father-SpouseName1': investor.father_name[:24],
        'Father-SpouseName2': investor.father_name[24:48]if len(investor.father_name[24:]) > 24 else investor.father_name[24:],
        'Fax': None,
        'GenderFemale': True if user.gender == 'F' else False,
        'GenderMale': True if user.gender == 'M' else False,
        'IDProof-Aadhar': False,
        'IDProof-DriversLicense': False,
        'IDProof-Other': False,
        'IDProof-Other-Specify': None,
        'IDProof-Passport': False,
        'IDProof-VoterID': False,
        'MaritalStatus-Married': True if user.marital_status == '2' else False,
        'MaritalStatus-Single': True if user.marital_status == '1' else False,
        'Name1': investor.applicant_name[:31],
        'Name2': investor.applicant_name[31:62]if len(investor.applicant_name[31:]) > 31 else investor.applicant_name[31:],
        'Nationality-Indian': True,
        'Nationality-Other': False,
        'Nationality-Other-Specify': None,
        'PAN': investor.pan_number,
        'PermanentAddress-City': permanent_address.pincode.city if not contact.address_are_equal else None,
        'PermanentAddress-Country': user.nationality if not contact.address_are_equal else None,
        'PermanentAddress-Pincode': permanent_address.pincode.pincode if not contact.address_are_equal else None,
        'PermanentAddress-State': permanent_address.pincode.state if not contact.address_are_equal else None,
        'PermanentAddress1': permanent_address.address_line_1 if not contact.address_are_equal else None,
        'PermanentAddress2': permanent_address.address_line_2 if not contact.address_are_equal else None,
        'PermanentAddress3': None,
        'PermanentAddressProof-BankStatement': True if contact.address_proof_type == 5 else False,
        'PermanentAddressProof-DriversLicense': True if contact.address_proof_type == 2 else False,
        'PermanentAddressProof-ElectricityBill': True if contact.address_proof_type == 6 else False,
        'PermanentAddressProof-GasBill': True if contact.address_proof_type == 6 else False,
        'PermanentAddressProof-LeaseAgreement': False,
        'PermanentAddressProof-Other': False,
        'PermanentAddressProof-Other-Specify': None,
        'PermanentAddressProof-Passport': True if contact.address_proof_type == 1 else False,
        'PermanentAddressProof-RationCard': True if contact.address_proof_type == 7 else False,
        'PermanentAddressProof-TelBill': True if contact.address_proof_type == 6 else False,
        'PermanentAddressProof-VoterID': True if contact.address_proof_type == 3 else False,
        'PermanentAddressProof-dd': None,  # TODO to be filled by Rashmi
        'PermanentAddressProof-mm': None,
        'PermanentAddressProof-yyyy': None,
        'SignatureDate': curr_date.strftime('%d/%m/%Y'),
        'SignaturePlace': contact.communication_address.pincode.city,
        'Status-ForeignNational': False,
        'Status-NonResident': False,
        'Status-Resident': True,
        'Tel-Mobile': contact.phone_number,
        'Tel-Off': None,
        'Tel-Residence': None,
    }

    for key, value in kyc_dict.items():
        if value is None:
            kyc_dict[key] = ""
        if value is True:
            kyc_dict[key] = "Yes"
        if value is False:
            kyc_dict[key] = "Off"

    for key, value in kyc_dict.items():
        if value not in ("", "Yes", "Off"):
            if type(value) == str:
                if "@" in value:
                    continue
            kyc_dict[key] = str(value).upper()

    fields = [(key, value) for key, value in kyc_dict.items()]

    return fields



def kyc_fdf_generator_new(user, investor, nominee, contact, investor_bank, curr_date):


    permanent_address = {
        'pincode': {'city': None, 'state': None, 'pincode': None},
        'address_line_1': None,
        'address_line_2': None
    }

    if contact.permanent_address is not None:
        permanent_address = contact.permanent_address
    
    first_name,middle_name,last_name = full_name_split(investor.applicant_name)
    father_first_name,father_middle_name,father_last_name = full_name_split(investor.father_name)
    mother_first_name,mother_middle_name,mother_last_name = full_name_split(investor.mother_name)
    maiden_first_name,maiden_middle_name,maiden_last_name = full_name_split(investor.maiden_name)
    
    kyc_dict = {
        'Aadhar-Number': None,
        'Birth-dd': investor.dob.strftime("%d"),
        'Birth-mm': investor.dob.strftime("%m"),
        'Birth-yyyy': investor.dob.strftime("%Y"),
        'CorrespondenceAddress-City': None if contact.address_are_equal else contact.communication_address.pincode.city,
        'CorrespondenceAddress-Pincode': None if contact.address_are_equal else  contact.communication_address.pincode.pincode,
        'CorrespondenceAddress-State': None if contact.address_are_equal else contact.communication_address.pincode.state,
        'CorrespondenceAddress-Country': None if contact.address_are_equal else  "INDIA",
        'CorrespondenceAddress1': None if contact.address_are_equal else  contact.communication_address.address_line_1,
        'CorrespondenceAddress2': None if contact.address_are_equal else  contact.communication_address.address_line_2,
        'CorrespondenceAddress3': None,
        'CorrespondenceAddress-Same':True if contact.address_are_equal else False,
        'CorrespondenceAddress-CountryCode':'',
        'CorrespondenceAddress-District':'',
        'CorrespondenceAddress-StateCode':'',
        'Code_4':'',
        'Country-Residence':'',
        'Country-Residence-Code':'',
        'CountryOfBirth':'',
        'EmailID': contact.email,
        'Father_Spouse_prefix':'',
        'father_spouse_first_name': father_first_name,
        'father_spouse_middle_name': father_middle_name,
        'father_spouse_last_name': father_last_name,
        'name_prefix':'',
        'First_Name': first_name,
        'Middle_Name': middle_name,
        'Last_Name':last_name,
        'ForeignAddress-City':'',
        'ForeignAddress-Country':'',
        'ForeignAddress-CountryCode':'',
        'ForeignAddress-Pincode':'',
        'ForeignAddress-State':'',
        'ForeignAddress-StateCode':'',
        'ForeignAddress1':'',
        'ForeignAddress2':'',
        'ForeignAddress3':'',
        'ForeignResidence':'',
        'Fax': None,
        'GenderFemale': True if user.gender == 'F' else False,
        'GenderMale': True if user.gender == 'M' else False,
        'Transgender':False,
        'IDProof-Aadhar': False,
        'IDProof-DriversLicense': False,
        'IDProof-Other': False,
        'IDProof-Other-Specify': None,
        'IDProof-Passport': False,
        'IDProof-VoterID': False,
        'IDProof-NREGA':False,
        
        'KYCType-Normal':True,
        'New':True,
        'Update':False,
        'KYC Number':None,
        
        'MaritalStatus-Married': True if user.marital_status == '2' else False,
        'MaritalStatus-Single': True if user.marital_status == '1' else False,
        'MaritalStatus-Others':False,
        'mother_prefix':'',
        'mother_first_name':mother_first_name,
        'mother_middle_name':mother_middle_name,
        'mother_last_name':mother_last_name,
        'maiden_name_prefix':'',
        'maiden_first_name':'',
        'maiden_first_name':'',
        'maiden_first_name':'',
        'Nationality-Indian': True,
        'Nationality-Other': False,
        'Nationality-Other-Specify': None,
        'Nationality-Other-Code':None,
        'PAN': investor.pan_number,
        'Passport-Number':None,
        'PermanentAddress-City': contact.communication_address.pincode.city if contact.address_are_equal else permanent_address.pincode.city ,
        'PermanentAddress-Country': user.nationality,
        'PermanentAddress-Pincode': contact.communication_address.pincode.pincode if contact.address_are_equal else permanent_address.pincode.pincode,
        'PermanentAddress-State': contact.communication_address.pincode.state if contact.address_are_equal else permanent_address.pincode.state,
        'PermanentAddress1': contact.communication_address.address_line_1 if contact.address_are_equal else permanent_address.address_line_1 ,
        'PermanentAddress2': contact.communication_address.address_line_2 if contact.address_are_equal else permanent_address.address_line_2 ,
        'PermanentAddress3': None,
        'PermanentAddress-CountryCode':'',
        'PermanentAddress-District':'',
        'PermanentAddress-StateCode':'',
        'PermanentAddressType-Business':True if contact.communication_address_type == 2 else False,
        'PermanentAddressType-RegisteredOffice':True if contact.communication_address_type == 4 else False,
        'PermanentAddressType-Residential':True if contact.communication_address_type == 1 else False,
        'PermanentAddressType-ResidentialBusiness':True if contact.communication_address_type == 3 else False,
        'PermanentAddressType-Other':True if contact.communication_address_type is None else False,
        
        'PermanentAddressProof-DriversLicense': True if contact.address_proof_type == 2 else False,
        'PermanentAddressProof-Other': True if contact.address_proof_type in [4,5,6,7,8] else False,
        'PermanentAddressProof-Other-Specify': None,
        'PermanentAddressProof-Passport': True if contact.address_proof_type == 1 else False,
        'PermanentAddressProof-VoterID': True if contact.address_proof_type == 3 else False,
        
        'Occupation-Private':True if investor.occupation_type == "PRI" else False,
        'Occupation-Professional':True if investor.occupation_type == "PRO" else False,
        'Occupation-Business':True if investor.occupation_type == "BUS" else False,
        'Occupation-Housewife':True if investor.occupation_type == "HOU" else False,
        'Occupation-Public':True if investor.occupation_type == "PUB" else False,
        'Occupation-Govt':True if investor.occupation_type == "GOV" else False,
        'Occupation-Retired':True if investor.occupation_type == "RET" else False,
        'Occupation-ForexDealer':True if investor.occupation_type == "FOR" else False,
        'Occupation-Agriculturist':True if investor.occupation_type == "AGR" else False,
        'Occupation-Student':True if investor.occupation_type == "STU" else False,
        'Occupation_Other':True if investor.occupation_type == "OTH" else False,
        'Signature-dd':curr_date.strftime('%d'),
        'Signature-mm':curr_date.strftime('%m'),
        'Signature-yyyy':curr_date.strftime('%Y'),
        'SignaturePlace': contact.communication_address.pincode.city,
        'Status-ForeignNational': False,
        'Status-NonResident': False,
        'Status-Resident': True,
        'Status-PIO':False,
        'Tel-Mobile-Code':None, #contact.phone_country_code
        'Tel-Mobile': contact.phone_number,
        'Tel-Off': None,
        'Tel-Residence': None,
    }

    for key, value in kyc_dict.items():
        if value is None:
            kyc_dict[key] = ""
        if value is True:
            kyc_dict[key] = "Yes"
        if value is False:
            kyc_dict[key] = "Off"

    for key, value in kyc_dict.items():
        if value not in ("", "Yes", "Off"):
            if type(value) == str:
                if "@" in value:
                    continue
            kyc_dict[key] = str(value).upper()

    fields = [(key, value) for key, value in kyc_dict.items()]

    return fields


