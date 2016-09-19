# XPATHS FOR READING NSE_RESPONSE FIELDS

RESPONSE_BASE_PATH = './{urn:schemas-microsoft-com:xml-diffgram-v1}diffgram/NMFIISERVICES'

SERVICE_RETURN_CODE_PATH = './service_status/service_return_code'
SERVICE_RETURN_ERROR_MSG_PATH = './return_msg'
SERVICE_RESPONSE_VALUE_PATH = './service_response'

# XPATHS FOR UPDATING NSE_REQUEST FIELDS

SERVICE_REQUEST_PATH = './service_request'

# COMMON XPATHS

APPLN_ID_PATH = './appln_id'
PASSWORD_PATH = './password'
BROKER_CODE_XPATH = './broker_code'

# for GETIIN
IIN_XPATH = './iin'

GUARDIAN_PAN_XPATH = ''
JH1_EXEMPT_FLAG_XPATH = ''
JH2_EXEMPT_FLAG_XPATH = ''
EXEMPT_FLAG_XPATH = ''

# for CREATECUSTOMER
TITLE_XPATH = './title'
INV_NAME_XPATH = './inv_name'
PAN_XPATH = './pan'
VALID_PAN_XPATH = './valid_pan'
EXEMPTION_XPATH = './exemption'
EXEMPT_CATEGORY_XPATH = './exempt_category'
EXEMPT_REF_NO_XPATH = './exempt_ref_no'
DOB_XPATH = './dob'
HOLD_NATURE_XPATH = './hold_nature'
TAX_STATUS_XPATH = './tax_status'
KYC_XPATH = './kyc'
OCCUPATION_XPATH = './occupation'
MFU_CAN_XPATH = './mfu_can'
DP_ID_XPATH = './dp_id'
FATHER_NAME_XPATH = './father_name'
MOTHER_NAME_XPATH = './mother_name'
TRXN_ACCEPTANCE_XPATH = './trxn_acceptance'
ADDR1_XPATH = './addr1'
ADDR2_XPATH = './addr2'
ADDR3_XPATH = './addr3'
CITY_XPATH = './city'
STATE_XPATH = './state'
PINCODE_XPATH = './pincode'
COUNTRY_XPATH = './country'
MOBILE_XPATH = './mobile_no'
RES_PHONE_XPATH = './res_phone'
OFF_PHONE_XPATH = './off_phone'
RES_FAX_XPATH = './res_fax'
OFF_FAX_XPATH = './off_fax'
EMAIL_XPATH = './email'
NRI_ADDR1_XPATH = './nri_addr1'
NRI_ADDR2_XPATH = './nri_addr2'
NRI_ADDR3_XPATH = './nri_addr3'
NRI_CITY_XPATH = './nri_city'
NRI_STATE_XPATH = './nri_state'
NRI_PINCODE_XPATH = './nri_pincode'
NRI_COUNTRY_XPATH = './nri_country'
BANK_NAME_XPATH = './bank_name'
ACC_NO_XPATH = './acc_no'
ACC_TYPE_XPATH = './acc_type'
IFSC_CODE_XPATH = './ifsc_code'
BRANCH_NAME_XPATH = './branch_name'
BRANCH_ADDR1_XPATH = './branch_addr1'
BRANCH_ADDR2_XPATH = './branch_addr2'
BRANCH_ADDR3_XPATH = './branch_addr3'
BRANCH_CITY_XPATH = './branch_city'
BRANCH_PINCODE_XPATH = './branch_pincode'
BRANCH_COUNTRY_XPATH = './branch_country'
JH1_NAME_XPATH = './jh1_name'
JH1_PAN_XPATH = './jh1_pan'
JH1_VALID_PAN_XPATH = './jh1_valid_pan'
JH1_EXEMPTION_XPATH = './jh1_exemption'
JH1_EXEMPT_CATEGORY_XPATH = './jh1_exempt_category'
JH1_EXEMPT_REF_NO_XPATH = './jh1_exempt_ref_no'
JH1_DOB_XPATH = './jh1_dob'
JH1_KYC_XPATH = './jh1_kyc'
JH2_NAME_XPATH = './jh2_name'
JH2_PAN_XPATH = './jh2_pan'
JH2_VALID_PAN_XPATH = './jh2_valid_pan'
JH2_EXEMPTION_XPATH = './jh2_exemption'
JH2_EXEMPT_CATEGORY_XPATH = './jh2_exempt_category'
JH2_EXEMPT_REF_NO_XPATH = './jh2_exempt_ref_no'
JH2_DOB_XPATH = './jh2_dob'
JH2_KYC_XPATH = './jh2_kyc'
NO_OF_NOMINEE_XPATH = './no_of_nominee'
NOMINEE1_TYPE_XPATH = './nominee1_type'
NOMINEE1_NAME_XPATH = './nominee1_name'
NOMINEE1_DOB_XPATH = './nominee1_dob'
NOMINEE1_ADDR1_XPATH = './nominee1_addr1'
NOMINEE1_ADDR2_XPATH = './nominee1_addr2'
NOMINEE1_ADDR3_XPATH = './nominee1_addr3'
NOMINEE1_CITY_XPATH = './nominee1_city'
NOMINEE1_STATE_XPATH = './nominee1_state'
NOMINEE1_PINCODE_XPATH = './nominee1_pincode'
NOMINEE1_RELATION_XPATH = './nominee1_relation'
NOMINEE1_PERCENT_XPATH = './nominee1_percent'
NOMINEE1_GUARD_NAME_XPATH = './nominee1_guard_name'
NOMINEE1_GUARD_PAN_XPATH = './nominee1_guard_pan'
NOMINEE2_TYPE_XPATH = './nominee2_type'
NOMINEE2_NAME_XPATH = './nominee2_name'
NOMINEE2_DOB_XPATH = './nominee2_dob'
NOMINEE2_RELATION_XPATH = './nominee2_relation'
NOMINEE2_PERCENT_XPATH = './nominee2_percent'
NOMINEE2_GUARD_NAME_XPATH = './nominee2_guard_name'
NOMINEE2_GUARD_PAN_XPATH = './nominee2_guard_pan'
NOMINEE3_TYPE_XPATH = './nominee3_type'
NOMINEE3_NAME_XPATH = './nominee3_name'
NOMINEE3_DOB_XPATH = './nominee3_dob'
NOMINEE3_RELATION_XPATH = './nominee3_relation'
NOMINEE3_PERCENT_XPATH = './nominee3_percent'
NOMINEE3_GUARD_NAME_XPATH = './nominee3_guard_name'
NOMINEE3_GUARD_PAN_XPATH = './nominee3_guard_pan'
GUARD_NAME_XPATH = './guard_name'
GUARD_PAN_XPATH = './guard_pan'
GUARD_VALID_PAN_XPATH = './guard_valid_pan'
GUARD_EXEMPTION_XPATH = './guard_exemption'
GUARD_EXEMPT_CATEGORY_XPATH = './guard_exempt_category'
GUARD_PAN_REF_NO_XPATH = './guard_pan_ref_no'
GUARD_DOB_XPATH = './guard_dob'
GUARD_KYC_XPATH = './guard_kyc'

# for PURCHASETXN

CHILD_TRANS_XPATH = './childtrans'
AMC_XPATH = './amc'
FOLIO_XPATH = './folio'
PRODUCT_CODE_XPATH = './product_code'
REINVEST_XPATH = './reinvest'
AMOUNT_XPATH = './amount'
SIP_FROM_DATE_XPATH = './sip_from_date'
SIP_END_DATE_XPATH = './sip_end_date'
SIP_FREQ_XPATH = './sip_freq'
SIP_AMOUNT_XPATH = './sip_amount'
SIP_PERIOD_DAY_XPATH = './sip_period_day'

SUB_TRXN_TYPE_XPATH = './sub_trxn_type'
POA_XPATH = './poa'
TRXN_ACCEPTANCE_XPATH = './trxn_acceptance'
DEMAT_USER_XPATH = './demat_user'
BANK_XPATH = './bank'
AC_NO_XPATH = './ac_no'
SUB_BROKER_ARN_CODE_XPATH = './sub_broker_arn_code'
SUB_BROKER_CODE_XPATH = './sub_broker_code'
EUIN_OPTED_XPATH = './euin_opted'
EUIN_XPATH = './euin'
TRXN_EXECUTION_XPATH = './trxn_execution'
REMARKS_XPATH = './remarks'
PAYMENT_MODE_XPATH = './payment_mode'
BILLDESK_BANK_XPATH = './billdesk_bank'
INSTRM_BANK_XPATH = './instrm_bank'
INSTRM_AC_NO_XPATH = './instrm_ac_no'
INSTRM_NO_XPATH = './instrm_no'
INSTRM_AMOUNT_XPATH = './instrm_amount'
INSTRM_DATE_XPATH = './instrm_date'
INSTRM_BRANCH_XPATH = './instrm_branch'
INSTRM_CHARGES_XPATH = './instrm_charges'
MICR_XPATH = './micr'
MICR_NO_XPATH = './micr_no'
RTGS_CODE_XPATH = './rtgs_code'
NEFT_IFSC_XPATH = './neft_ifsc'
ADVISIORY_CHARGE_XPATH = './advisory_charge'
DD_CHARGE_XPATH = './dd_charge'
CHEQUE_DEPOSIT_MODE_XPATH = './cheque_deposit_mode'
DEBIT_AMOUNT_TYPE_XPATH = './debit_amount_type'
NOMINEE_FLAG_XPATH = './nominee_flag'
SIP_MICR_NO_XPATH = './sip_micr_no'
SIP_BANK_XPATH = './sip_bank'
SIP_BRANCH_XPATH = './sip_branch'
SIP_ACC_NO_XPATH = './sip_acc_no'
SIP_AC_TYPE_XPATH = './sip_ac_type'
SIP_IFSC_CODE_XPATH = './sip_ifsc_code'
UMRN_XPATH = './umrn'
ACH_AMT_XPATH = './ach_amt'
ACH_AMOUNT_XPATH = './ach_amount'
ACH_FROM_DATE_XPATH = './ach_fromdate'
ACH_TO_DATE_XPATH = './ach_todate'
ACH_END_DATE_XPATH = './ach_enddate'
UNTIL_CANCELLED_XPATH = './until_cancelled'
RETURN_PAYMENT_FLAG_XPATH = './Return_paymnt_flag'
CLIENT_CALLBACK_URL_XPATH = './Client_callback_url'
TRANS_COUNT_XPATH = './trans_count'
UC_XPATH = './uc'

# NSE VARIABLES

RETURN_CODE_FAILURE = '1'

RETURN_CODE_SUCCESS = '0'

NSE_NMF_BASE_API_URL = "http://124.124.236.198/NMFIITrxnService/NMFTrxnService/"
NSE_NMF_APPL_ID = "MFS108537"
NSE_NMF_PASSWORD = "test$258"
NSE_NMF_BROKER_CODE = "ARN-108537"

# NSE REQUEST XML

METHOD_CREATECUSTOMER = "CREATECUSTOMER"
METHOD_IINDETAILS = "IINDETAILS"
METHOD_PURCHASETXN = "PURCHASETRXN"
METHOD_UPLOADIMG = "UPLOADIMG"
METHOD_GETIIN = "GETIIN"
METHOD_ACHMANDATEREGISTRATIONS = "ACHMANDATEREGISTRATIONS"

REQUEST_CREATECUSTOMER = '''<NMFIIService>
                    <service_request>
                        <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                        <password>''' + NSE_NMF_PASSWORD + '''</password>
                        <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                        <title></title>
                        <inv_name></inv_name>
                        <pan></pan>
                        <valid_pan></valid_pan>
                        <exemption></exemption>
                        <exempt_category></exempt_category>
                        <exempt_ref_no></exempt_ref_no>
                        <dob></dob>
                        <hold_nature></hold_nature>
                        <tax_status></tax_status>
                        <kyc></kyc>
                        <occupation></occupation>
                        <mfu_can></mfu_can>
                        <dp_id></dp_id>
                        <father_name></father_name>
                        <mother_name></mother_name>
                        <trxn_acceptance></trxn_acceptance>
                        <addr1></addr1>
                        <addr2></addr2>
                        <addr3></addr3>
                        <city></city>
                        <state></state>
                        <pincode></pincode>
                        <country></country>
                        <mobile_no></mobile_no>
                        <res_phone></res_phone>
                        <off_phone></off_phone>
                        <res_fax></res_fax>
                        <off_fax></off_fax>
                        <email></email>
                        <nri_addr1></nri_addr1>
                        <nri_addr2></nri_addr2>
                        <nri_addr3></nri_addr3>
                        <nri_city></nri_city>
                        <nri_state></nri_state>
                        <nri_pincode></nri_pincode>
                        <nri_country></nri_country>
                        <bank_name></bank_name>
                        <acc_no></acc_no>
                        <acc_type></acc_type>
                        <ifsc_code></ifsc_code>
                        <branch_name></branch_name>
                        <branch_addr1></branch_addr1>
                        <branch_addr2></branch_addr2>
                        <branch_addr3></branch_addr3>
                        <branch_city></branch_city>
                        <branch_pincode></branch_pincode>
                        <branch_country></branch_country>
                        <jh1_name></jh1_name>
                        <jh1_pan></jh1_pan>
                        <jh1_valid_pan></jh1_valid_pan>
                        <jh1_exemption></jh1_exemption>
                        <jh1_exempt_category></jh1_exempt_category>
                        <jh1_exempt_ref_no></jh1_exempt_ref_no>
                        <jh1_dob></jh1_dob>
                        <jh1_kyc></jh1_kyc>
                        <jh2_name></jh2_name>
                        <jh2_pan></jh2_pan>
                        <jh2_valid_pan></jh2_valid_pan>
                        <jh2_exemption></jh2_exemption>
                        <jh2_exempt_category></jh2_exempt_category>
                        <jh2_exempt_ref_no></jh2_exempt_ref_no>
                        <jh2_dob></jh2_dob>
                        <jh2_kyc></jh2_kyc>
                        <no_of_nominee></no_of_nominee>
                        <nominee1_type></nominee1_type>
                        <nominee1_name></nominee1_name>
                        <nominee1_dob></nominee1_dob>
                        <nominee1_addr1></nominee1_addr1>
                        <nominee1_addr2></nominee1_addr2>
                        <nominee1_addr3></nominee1_addr3>
                        <nominee1_city></nominee1_city>
                        <nominee1_state></nominee1_state>
                        <nominee1_pincode></nominee1_pincode>
                        <nominee1_relation></nominee1_relation>
                        <nominee1_percent></nominee1_percent>
                        <nominee1_guard_name></nominee1_guard_name>
                        <nominee1_guard_pan></nominee1_guard_pan>
                        <nominee2_type></nominee2_type>
                        <nominee2_name></nominee2_name>
                        <nominee2_dob></nominee2_dob>
                        <nominee2_relation></nominee2_relation>
                        <nominee2_percent></nominee2_percent>
                        <nominee2_guard_name></nominee2_guard_name>
                        <nominee2_guard_pan></nominee2_guard_pan>
                        <nominee3_type></nominee3_type>
                        <nominee3_Name></nominee3_Name>
                        <nominee3_dob></nominee3_dob>
                        <nominee3_relation></nominee3_relation>
                        <nominee3_percent></nominee3_percent>
                        <nominee3_guard_name></nominee3_guard_name>
                        <nominee3_guard_pan></nominee3_guard_pan>
                        <guard_name></guard_name>
                        <guard_pan></guard_pan>
                        <guard_valid_pan></guard_valid_pan>
                        <guard_exemption></guard_exemption>
                        <guard_exempt_category></guard_exempt_category>
                        <guard_pan_ref_no></guard_pan_ref_no>
                        <guard_dob></guard_dob>
                        <guard_kyc></guard_kyc>
                    </service_request>
                </NMFIIService>'''

REQUEST_GETIIN = '''<NMFIIService>
                    <service_request>
                    <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                    <password>''' + NSE_NMF_PASSWORD + '''</password>
                    <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                    <tax_status></tax_status>
                    <hold_nature></hold_nature>
                    <exempt_flag></exempt_flag>
                    <fh_pan></fh_pan>
                    <jh1_exempt_flag></jh1_exempt_flag>
                    <jh1_pan></jh1_pan>
                    <jh2_exempt_flag></jh2_exempt_flag>
                    <jh2_pan></jh2_pan>
                    <guardian_pan></guardian_pan>
                    </service_request>
                </NMFIIService>'''

REQUEST_IINDETAILS = '''<NMFIIService>
                        <service_request>
                        <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                        <password>''' + NSE_NMF_PASSWORD + '''</password>
                        <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                        <iin></iin>
                        </service_request>
                    </NMFIIService>'''

REQUEST_PURCHASETXN = '''<NMFIIService>
                            <service_request>
                            <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                            <password>''' + NSE_NMF_PASSWORD + '''</password>
                            <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                            <iin></iin>
                            <sub_trxn_type></sub_trxn_type>
                            <poa></poa>
                            <trxn_acceptance></trxn_acceptance>
                            <demat_user></demat_user>
                            <dp_id></dp_id>
                            <bank></bank>
                            <ac_no></ac_no>
                            <ifsc_code></ifsc_code>
                            <sub_broker_arn_code></sub_broker_arn_code>
                            <sub_broker_code></sub_broker_code>
                            <euin_opted></euin_opted>
                            <euin></euin>
                            <trxn_execution></trxn_execution>
                            <remarks></remarks>
                            <payment_mode></payment_mode>
                            <billdesk_bank></billdesk_bank>
                            <instrm_bank></instrm_bank>
                            <instrm_ac_no></instrm_ac_no>
                            <instrm_no></instrm_no>
                            <instrm_amount></instrm_amount>
                            <instrm_date></instrm_date>
                            <instrm_branch></instrm_branch>
                            <instrm_charges><instrm_charges>
                            <micr></micr>
                            <rtgs_code></rtgs_code>
                            <neft_ifsc></neft_ifsc>
                            <advisory_charge> </advisory_charge>
                            <dd_charge></dd_charge>
                            <cheque_deposit_mode></cheque_deposit_mode>
                            <debit_amount_type></debit_amount_type>
                            <nominee_flag></nominee_flag>
                            <no_of_nominee></no_of_nominee>
                            <nominee1_name></nominee1_name>
                            <nominee1_dob></nominee1_dob>
                            <nominee1_addr1></nominee1_addr1>
                            <nominee1_addr2></nominee1_addr2>
                            <nominee1_addr3></nominee1_addr3>
                            <nominee1_city></nominee1_city>
                            <nominee1_state></nominee1_state>
                            <nominee1_pincode></nominee1_pincode>
                            <nominee1_relation></nominee1_relation>
                            <nominee1_percent></nominee1_percent>
                            <nominee1_guard_name></nominee1_guard_name>
                            <nominee1_guard_pan></nominee1_guard_pan>
                            <nominee2_name></nominee2_name>
                            <nominee2_dob></nominee2_dob>
                            <nominee2_relation><nominee2_relation>
                            <nominee2_percent><nominee2_percent>
                            <nominee2_guard_name></nominee2_guard_name>
                            <nominee2_guard_pan></nominee2_guard_pan>
                            <nominee3_Name></nominee3_Name>
                            <nominee3_dob></nominee3_dob>
                            <nominee3_relation></nominee3_relation>
                            <nominee3_percent></nominee3_percent>
                            <nominee3_guard_name></nominee3_guard_name>
                            <nominee3_guard_pan></nominee3_guard_pan>
                            <sip_micr_no></sip_micr_no>
                            <sip_bank></sip_bank>
                            <sip_branch></sip_branch>
                            <sip_acc_no></sip_acc_no>
                            <sip_ac_type></sip_ac_type>
                            <sip_ifsc_code></sip_ifsc_code>
                            <umrn> </umrn>
                            <ach_amt></ach_amt>
                            <ach_fromdate></ach_fromdate>
                            <ach_enddate></ach_enddate>
                            <until_cancelled></until_cancelled>
                            <Return_paymnt_flag></Return_paymnt_flag>
                            <Client_callback_url></Client_callback_url>
                            <trans_count></trans_count>
                            </service_request>
                            <childtrans>
                                <amc></amc>
                                <folio></folio>
                                <product_code></product_code>
                                <reinvest></reinvest>
                                <amount></amount>
                                <sip_from_date></sip_from_date>
                                <sip_end_date></sip_end_date>
                                <sip_freq></sip_freq>
                                <sip_amount></sip_amount>
                                <sip_period_day></sip_period_day>
                            </childtrans>
                        </NMFIIService>'''

REQUEST_ACHMANDATEREGISTRATIONS = '''<NMFIIService>
                                         <service_request>
                                            <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                                            <password>''' + NSE_NMF_PASSWORD + '''</password>
                                            <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                                            <iin></iin>
                                            <acc_no></acc_no>
                                            <acc_type></acc_type>
                                            <ifsc_code></ifsc_code>
                                            <bank_name></bank_name>
                                            <branch_name></branch_name>
                                            <micr_no></micr_no>
                                            <uc></uc>
                                            <ach_fromdate></ach_fromdate>
                                            <ach_todate></ach_todate>
                                            <ach_amount></ach_amount>
                                        </service_request>
                                    </NMFIIService>'''
