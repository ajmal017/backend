from . import constants

class Address(object):
    def __init__(self, type=""):
        self.type = type
        self.addr1 = ""
        self.addr2 = ""
        self.addr3 = ""
        self.city = ""
        self.state = ""
        self.pincode = ""
        self.country = ""

class Info(object):
    def __init__(self, type=""):
        self.type = type
        self.name = ""
        self.pan = ""
        self.valid_pan = ""
        self.exemption = ""
        self.exempt_category = ''
        self.exempt_ref_no = ''
        self.dob = ''
        self.kyc = ''

class IINDetails(object):

    def __init__(self, element):
        self.title = ""
        self.inv_name = ""
        self.pan = ""
        self.valid_pan = ""
        self.exemption = ""
        self.exempt_category = ""
        self.exempt_ref_no = ""
        self.dob = ""
        self.hold_nature = ""
        self.tax_status = ""
        self.kyc = ""
        self.occupation = ""
        self.mfu_can = ""
        self.dp_id = ""
        self.father_name = ""
        self.mother_name = ""
        self.trxn_acceptance = ""
        self.mobile_no = ""
        self.res_phone = ""
        self.off_phone = ""
        self.res_fax = ""
        self.off_fax = ""
        self.email = ""
        self.bank_name = ""
        self.acc_type = ""
        self.ifsc_code = ""
        self.branch_name = ""
        self.acc_no = ""
        self.user_address = Address()
        self.nri_address = Address("nri")
        self.branch_address = Address("branch")
        self.jh1_info = Info("jh1")
        self.jh2_info = Info("jh2")
        self.no_of_nominee = ''
        self.guard_info = Info("guard")