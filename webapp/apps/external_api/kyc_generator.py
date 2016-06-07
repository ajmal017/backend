
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
