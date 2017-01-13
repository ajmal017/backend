NO_DATA_FOUND = 'No Data Found'

PAYMENT_RU = "https://api.finaskus.com/v3.0/core/billdesk/nse/complete/"

# XPATHS FOR READING NSE_RESPONSE FIELDS

RESPONSE_BASE_PATH = './{urn:schemas-microsoft-com:xml-diffgram-v1}diffgram/NMFIISERVICES'

SERVICE_RETURN_CODE_PATH = './service_status/service_return_code'
SERVICE_RETURN_ERROR_MSG_PATH = './return_msg'
SERVICE_RESPONSE_VALUE_PATH = './service_response'
SERVICE_RETURN_MSG_PATH = SERVICE_RESPONSE_VALUE_PATH + '/return_msg'
RESPONSE_PAYMENT_LINK_PATH = SERVICE_RETURN_MSG_PATH + './paymentlink'

# XPATHS FOR UPDATING NSE_REQUEST FIELDS

SERVICE_REQUEST_PATH = './service_request'

# COMMON XPATHS

APPLN_ID_PATH = './appln_id'
PASSWORD_PATH = './password'
BROKER_CODE_XPATH = './broker_code'

# for GETIIN
IIN_XPATH = SERVICE_REQUEST_PATH + '/iin'

JH1_EXEMPT_FLAG_XPATH = SERVICE_REQUEST_PATH + '/jh1_exempt_flag'
JH2_EXEMPT_FLAG_XPATH = SERVICE_REQUEST_PATH + '/jh2_exempt_flag'
EXEMPT_FLAG_XPATH = SERVICE_REQUEST_PATH + '/exempt_flag'
FH_PAN_XPATH = SERVICE_REQUEST_PATH + '/fh_pan'

# for CREATECUSTOMER
TITLE_XPATH = SERVICE_REQUEST_PATH + '/title'
INV_NAME_XPATH = SERVICE_REQUEST_PATH + '/inv_name'
PAN_XPATH = SERVICE_REQUEST_PATH + '/pan'
VALID_PAN_XPATH = SERVICE_REQUEST_PATH + '/valid_pan'
EXEMPTION_XPATH = SERVICE_REQUEST_PATH + '/exemption'
EXEMPT_CATEGORY_XPATH = SERVICE_REQUEST_PATH + '/exempt_category'
EXEMPT_REF_NO_XPATH = SERVICE_REQUEST_PATH + '/exempt_ref_no'
DOB_XPATH = SERVICE_REQUEST_PATH + '/dob'
HOLD_NATURE_XPATH = SERVICE_REQUEST_PATH + '/hold_nature'
TAX_STATUS_XPATH = SERVICE_REQUEST_PATH + '/tax_status'
KYC_XPATH = SERVICE_REQUEST_PATH + '/kyc'
OCCUPATION_XPATH = SERVICE_REQUEST_PATH + '/occupation'
MFU_CAN_XPATH = SERVICE_REQUEST_PATH + '/mfu_can'
DP_ID_XPATH = SERVICE_REQUEST_PATH + '/dp_id'
FATHER_NAME_XPATH = SERVICE_REQUEST_PATH + '/father_name'
MOTHER_NAME_XPATH = SERVICE_REQUEST_PATH + '/mother_name'
TRXN_ACCEPTANCE_XPATH = SERVICE_REQUEST_PATH + '/trxn_acceptance'
ADDR1_XPATH = SERVICE_REQUEST_PATH + '/addr1'
ADDR2_XPATH = SERVICE_REQUEST_PATH + '/addr2'
ADDR3_XPATH = SERVICE_REQUEST_PATH + '/addr3'
CITY_XPATH = SERVICE_REQUEST_PATH + '/city'
STATE_XPATH = SERVICE_REQUEST_PATH + '/state'
PINCODE_XPATH = SERVICE_REQUEST_PATH + '/pincode'
COUNTRY_XPATH = SERVICE_REQUEST_PATH + '/country'
MOBILE_XPATH = SERVICE_REQUEST_PATH + '/mobile_no'
RES_PHONE_XPATH = SERVICE_REQUEST_PATH + '/res_phone'
OFF_PHONE_XPATH = SERVICE_REQUEST_PATH + '/off_phone'
RES_FAX_XPATH = SERVICE_REQUEST_PATH + '/res_fax'
OFF_FAX_XPATH = SERVICE_REQUEST_PATH + '/off_fax'
EMAIL_XPATH = SERVICE_REQUEST_PATH + '/email'
NRI_ADDR1_XPATH = SERVICE_REQUEST_PATH + '/nri_addr1'
NRI_ADDR2_XPATH = SERVICE_REQUEST_PATH + '/nri_addr2'
NRI_ADDR3_XPATH = SERVICE_REQUEST_PATH + '/nri_addr3'
NRI_CITY_XPATH = SERVICE_REQUEST_PATH + '/nri_city'
NRI_STATE_XPATH = SERVICE_REQUEST_PATH + '/nri_state'
NRI_PINCODE_XPATH = SERVICE_REQUEST_PATH + '/nri_pincode'
NRI_COUNTRY_XPATH = SERVICE_REQUEST_PATH + '/nri_country'
BANK_NAME_XPATH = SERVICE_REQUEST_PATH + '/bank_name'
ACC_NO_XPATH = SERVICE_REQUEST_PATH + '/acc_no'
ACC_TYPE_XPATH = SERVICE_REQUEST_PATH + '/acc_type'
IFSC_CODE_XPATH = SERVICE_REQUEST_PATH + '/ifsc_code'
BRANCH_NAME_XPATH = SERVICE_REQUEST_PATH + '/branch_name'
BRANCH_XPATH = SERVICE_REQUEST_PATH + '/branch'
BRANCH_ADDR1_XPATH = SERVICE_REQUEST_PATH + '/branch_addr1'
BRANCH_ADDR2_XPATH = SERVICE_REQUEST_PATH + '/branch_addr2'
BRANCH_ADDR3_XPATH = SERVICE_REQUEST_PATH + '/branch_addr3'
BRANCH_CITY_XPATH = SERVICE_REQUEST_PATH + '/branch_city'
BRANCH_PINCODE_XPATH = SERVICE_REQUEST_PATH + '/branch_pincode'
BRANCH_COUNTRY_XPATH = SERVICE_REQUEST_PATH + '/branch_country'
JH1_NAME_XPATH = SERVICE_REQUEST_PATH + '/jh1_name'
JH1_PAN_XPATH = SERVICE_REQUEST_PATH + '/jh1_pan'
JH1_VALID_PAN_XPATH = SERVICE_REQUEST_PATH + '/jh1_valid_pan'
JH1_EXEMPTION_XPATH = SERVICE_REQUEST_PATH + '/jh1_exemption'
JH1_EXEMPT_CATEGORY_XPATH = SERVICE_REQUEST_PATH + '/jh1_exempt_category'
JH1_EXEMPT_REF_NO_XPATH = SERVICE_REQUEST_PATH + '/jh1_exempt_ref_no'
JH1_DOB_XPATH = SERVICE_REQUEST_PATH + '/jh1_dob'
JH1_KYC_XPATH = SERVICE_REQUEST_PATH + '/jh1_kyc'
JH2_NAME_XPATH = SERVICE_REQUEST_PATH + '/jh2_name'
JH2_PAN_XPATH = SERVICE_REQUEST_PATH + '/jh2_pan'
JH2_VALID_PAN_XPATH = SERVICE_REQUEST_PATH + '/jh2_valid_pan'
JH2_EXEMPTION_XPATH = SERVICE_REQUEST_PATH + '/jh2_exemption'
JH2_EXEMPT_CATEGORY_XPATH = SERVICE_REQUEST_PATH + '/jh2_exempt_category'
JH2_EXEMPT_REF_NO_XPATH = SERVICE_REQUEST_PATH + '/jh2_exempt_ref_no'
JH2_DOB_XPATH = SERVICE_REQUEST_PATH + '/jh2_dob'
JH2_KYC_XPATH = SERVICE_REQUEST_PATH + '/jh2_kyc'
NO_OF_NOMINEE_XPATH = SERVICE_REQUEST_PATH + '/no_of_nominee'
NOMINEE1_TYPE_XPATH = SERVICE_REQUEST_PATH + '/nominee1_type'
NOMINEE1_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee1_name'
NOMINEE1_DOB_XPATH = SERVICE_REQUEST_PATH + '/nominee1_dob'
NOMINEE1_ADDR1_XPATH = SERVICE_REQUEST_PATH + '/nominee1_addr1'
NOMINEE1_ADDR2_XPATH = SERVICE_REQUEST_PATH + '/nominee1_addr2'
NOMINEE1_ADDR3_XPATH = SERVICE_REQUEST_PATH + '/nominee1_addr3'
NOMINEE1_CITY_XPATH = SERVICE_REQUEST_PATH + '/nominee1_city'
NOMINEE1_STATE_XPATH = SERVICE_REQUEST_PATH + '/nominee1_state'
NOMINEE1_PINCODE_XPATH = SERVICE_REQUEST_PATH + '/nominee1_pincode'
NOMINEE1_RELATION_XPATH = SERVICE_REQUEST_PATH + '/nominee1_relation'
NOMINEE1_PERCENT_XPATH = SERVICE_REQUEST_PATH + '/nominee1_percent'
NOMINEE1_GUARD_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee1_guard_name'
NOMINEE1_GUARD_PAN_XPATH = SERVICE_REQUEST_PATH + '/nominee1_guard_pan'
NOMINEE2_TYPE_XPATH = SERVICE_REQUEST_PATH + '/nominee2_type'
NOMINEE2_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee2_name'
NOMINEE2_DOB_XPATH = SERVICE_REQUEST_PATH + '/nominee2_dob'
NOMINEE2_RELATION_XPATH = SERVICE_REQUEST_PATH + '/nominee2_relation'
NOMINEE2_PERCENT_XPATH = SERVICE_REQUEST_PATH + '/nominee2_percent'
NOMINEE2_GUARD_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee2_guard_name'
NOMINEE2_GUARD_PAN_XPATH = SERVICE_REQUEST_PATH + '/nominee2_guard_pan'
NOMINEE3_TYPE_XPATH = SERVICE_REQUEST_PATH + '/nominee3_type'
NOMINEE3_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee3_name'
NOMINEE3_DOB_XPATH = SERVICE_REQUEST_PATH + '/nominee3_dob'
NOMINEE3_RELATION_XPATH = SERVICE_REQUEST_PATH + '/nominee3_relation'
NOMINEE3_PERCENT_XPATH = SERVICE_REQUEST_PATH + '/nominee3_percent'
NOMINEE3_GUARD_NAME_XPATH = SERVICE_REQUEST_PATH + '/nominee3_guard_name'
NOMINEE3_GUARD_PAN_XPATH = SERVICE_REQUEST_PATH + '/nominee3_guard_pan'
GUARD_NAME_XPATH = SERVICE_REQUEST_PATH + '/guard_name'
GUARD_PAN_XPATH = SERVICE_REQUEST_PATH + '/guard_pan'
GUARDIAN_PAN_XPATH = SERVICE_REQUEST_PATH + '/guardian_pan'
GUARD_VALID_PAN_XPATH = SERVICE_REQUEST_PATH + '/guard_valid_pan'
GUARD_EXEMPTION_XPATH = SERVICE_REQUEST_PATH + '/guard_exemption'
GUARD_EXEMPT_CATEGORY_XPATH = SERVICE_REQUEST_PATH + '/guard_exempt_category'
GUARD_PAN_REF_NO_XPATH = SERVICE_REQUEST_PATH + '/guard_pan_ref_no'
GUARD_DOB_XPATH = SERVICE_REQUEST_PATH + '/guard_dob'
GUARD_KYC_XPATH = SERVICE_REQUEST_PATH + '/guard_kyc'

# for PURCHASETXN

CHILD_TRANS_XPATH = './childtrans'
AMC_XPATH = CHILD_TRANS_XPATH + '/amc'
FOLIO_XPATH = CHILD_TRANS_XPATH + '/folio'
PRODUCT_CODE_XPATH = CHILD_TRANS_XPATH + '/product_code'
TARGET_PRODUCT_XPATH = CHILD_TRANS_XPATH + '/target_product'
REINVEST_XPATH = CHILD_TRANS_XPATH + '/reinvest'
AMOUNT_XPATH = CHILD_TRANS_XPATH + '/amount'
FROM_DATE_XPATH = CHILD_TRANS_XPATH + '/from_date'
TO_DATE_XPATH = CHILD_TRANS_XPATH + '/to_date'
PERIODICITY_XPATH = CHILD_TRANS_XPATH + '/periodicity'
PERIOD_DAY_XPATH = CHILD_TRANS_XPATH + '/period_day'
SIP_FROM_DATE_XPATH = CHILD_TRANS_XPATH + '/sip_from_date'
SIP_END_DATE_XPATH = CHILD_TRANS_XPATH + '/sip_end_date'
SIP_FREQ_XPATH = CHILD_TRANS_XPATH + '/sip_freq'
SIP_AMOUNT_XPATH = CHILD_TRANS_XPATH + '/sip_amount'
SIP_PERIOD_DAY_XPATH = CHILD_TRANS_XPATH + '/sip_period_day'
SUB_TRXN_TYPE_XPATH = SERVICE_REQUEST_PATH + '/sub_trxn_type'
POA_XPATH = SERVICE_REQUEST_PATH + '/poa'
DEMAT_USER_XPATH = SERVICE_REQUEST_PATH + '/demat_user'
BANK_XPATH = SERVICE_REQUEST_PATH + '/bank'
AC_NO_XPATH = SERVICE_REQUEST_PATH + '/ac_no'
SUB_BROKER_ARN_CODE_XPATH = SERVICE_REQUEST_PATH + '/sub_broker_arn_code'
SUB_BROKER_CODE_XPATH = SERVICE_REQUEST_PATH + '/sub_broker_code'
SUB_BROK_ARN_XPATH = SERVICE_REQUEST_PATH + '/sub_brok_arn'
EUIN_OPTED_XPATH = SERVICE_REQUEST_PATH + '/euin_opted'
EUIN_XPATH = SERVICE_REQUEST_PATH + '/euin'
TRXN_EXECUTION_XPATH = SERVICE_REQUEST_PATH + '/trxn_execution'
REMARKS_XPATH = SERVICE_REQUEST_PATH + '/remarks'
PAYMENT_MODE_XPATH = SERVICE_REQUEST_PATH + '/payment_mode'
BILLDESK_BANK_XPATH = SERVICE_REQUEST_PATH + '/billdesk_bank'
INSTRM_BANK_XPATH = SERVICE_REQUEST_PATH + '/instrm_bank'
INSTRM_AC_NO_XPATH = SERVICE_REQUEST_PATH + '/instrm_ac_no'
INSTRM_NO_XPATH = SERVICE_REQUEST_PATH + '/instrm_no'
INSTRM_AMOUNT_XPATH = SERVICE_REQUEST_PATH + '/instrm_amount'
INSTRM_DATE_XPATH = SERVICE_REQUEST_PATH + '/instrm_date'
INSTRM_BRANCH_XPATH = SERVICE_REQUEST_PATH + '/instrm_branch'
INSTRM_CHARGES_XPATH = SERVICE_REQUEST_PATH + '/instrm_charges'
MICR_XPATH = SERVICE_REQUEST_PATH + '/micr'
MICR_NO_XPATH = SERVICE_REQUEST_PATH + '/micr_no'
RTGS_CODE_XPATH = SERVICE_REQUEST_PATH + '/rtgs_code'
NEFT_IFSC_XPATH = SERVICE_REQUEST_PATH + '/neft_ifsc'
ADVISIORY_CHARGE_XPATH = SERVICE_REQUEST_PATH + '/advisory_charge'
DD_CHARGE_XPATH = SERVICE_REQUEST_PATH + '/dd_charge'
CHEQUE_DEPOSIT_MODE_XPATH = SERVICE_REQUEST_PATH + '/cheque_deposit_mode'
DEBIT_AMOUNT_TYPE_XPATH = SERVICE_REQUEST_PATH + '/debit_amount_type'
DEBIT_AMT_TYPE_XPATH = SERVICE_REQUEST_PATH + '/debit_amt_type'
NOMINEE_FLAG_XPATH = SERVICE_REQUEST_PATH + '/nominee_flag'
SIP_PAYMECH_XPATH = SERVICE_REQUEST_PATH + '/sip_paymech'
SIP_MICR_NO_XPATH = SERVICE_REQUEST_PATH + '/sip_micr_no'
SIP_BANK_XPATH = SERVICE_REQUEST_PATH + '/sip_bank'
SIP_BRANCH_XPATH = SERVICE_REQUEST_PATH + '/sip_branch'
SIP_ACC_NO_XPATH = SERVICE_REQUEST_PATH + '/sip_acc_no'
SIP_AC_TYPE_XPATH = SERVICE_REQUEST_PATH + '/sip_ac_type'
SIP_IFSC_CODE_XPATH = SERVICE_REQUEST_PATH + '/sip_ifsc_code'
UMRN_XPATH = SERVICE_REQUEST_PATH + '/umrn'
ACH_AMT_XPATH = SERVICE_REQUEST_PATH + '/ach_amt'
ACH_AMOUNT_XPATH = SERVICE_REQUEST_PATH + '/ach_amount'
ACH_FROM_DATE_XPATH = SERVICE_REQUEST_PATH + '/ach_fromdate'
ACH_TO_DATE_XPATH = SERVICE_REQUEST_PATH + '/ach_todate'
ACH_END_DATE_XPATH = SERVICE_REQUEST_PATH + '/ach_enddate'
UNTIL_CANCELLED_XPATH = SERVICE_REQUEST_PATH + '/until_cancelled'
RETURN_PAYMENT_FLAG_XPATH = SERVICE_REQUEST_PATH + '/Return_paymnt_flag'
CLIENT_CALLBACK_URL_XPATH = SERVICE_REQUEST_PATH + '/Client_callback_url'
TRANS_COUNT_XPATH = SERVICE_REQUEST_PATH + '/trans_count'
UC_XPATH = SERVICE_REQUEST_PATH + '/uc'

REQUEST_IIN_XPATH = SERVICE_REQUEST_PATH + '/iin'
TRXN_NO_XPATH = SERVICE_REQUEST_PATH + '/trxn_no'
CEASE_REQ_DATE_XPATH = SERVICE_REQUEST_PATH + '/cease_req_date'
INSTBY_XPATH = SERVICE_REQUEST_PATH + '/initiated_by'
NIGO_REMARKS_XPATH = SERVICE_REQUEST_PATH + '/nigo_remarks'
AMOUNT_UNIT_TYPE_XPATH = SERVICE_REQUEST_PATH + '/amt_unit_type'
AMOUNT_UNIT_XPATH = SERVICE_REQUEST_PATH + '/amt_unit'
ALL_UNITS_XPATH = SERVICE_REQUEST_PATH + '/all_units'
ALL_UNIT_XPATH = SERVICE_REQUEST_PATH + '/all_unit'

# NSE VARIABLES

RETURN_CODE_FAILURE = '1'

RETURN_CODE_SUCCESS = '0'

NSE_NMF_BASE_URL = "http://124.124.236.198"
NSE_NMF_BASE_API_URL = NSE_NMF_BASE_URL + "/NMFIITrxnService/NMFTrxnService/"
NSE_NMF_UPLOAD_BASE_API_URL = NSE_NMF_BASE_URL + "/NMFIIImageUpload/ImageUpload/"
NSE_NMF_APPL_ID = "MFS108537"
NSE_NMF_PASSWORD = "test$258"
NSE_NMF_BROKER_CODE = "ARN-108537"

# NSE REQUEST XML

METHOD_CREATECUSTOMER = "CREATECUSTOMER"
METHOD_PURCHASETXN = "PURCHASETRXN"
METHOD_REDEEMTXN = "REDEEMTRXN"
METHOD_SYSTRXNREG = "SYSTRXNREG"
METHOD_UPLOADIMG = "UPLOADIMG"
METHOD_GETIIN = "GETIIN"
METHOD_ACHMANDATEREGISTRATIONS = "ACHMANDATEREGISTRATIONS"
METHOD_CEASESIP = "CEASESIP"

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
                        <nominee3_name></nominee3_name>
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

REQUEST_PURCHASE_CHILDTXN = '''<NMFIIService>
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
                            <instrm_charges></instrm_charges>
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
                            <nominee2_relation></nominee2_relation>
                            <nominee2_percent></nominee2_percent>
                            <nominee2_guard_name></nominee2_guard_name>
                            <nominee2_guard_pan></nominee2_guard_pan>
                            <nominee3_name></nominee3_name>
                            <nominee3_dob></nominee3_dob>
                            <nominee3_relation></nominee3_relation>
                            <nominee3_percent></nominee3_percent>
                            <nominee3_guard_name></nominee3_guard_name>
                            <nominee3_guard_pan></nominee3_guard_pan>
                            <sip_paymech></sip_paymech>
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
                        </NMFIIService>'''

REQUEST_SYSTRXNREG_CHILDTXN = '''<NMFIIService>
                                <childtrans>
                                    <amc></amc>
                                    <folio></folio>
                                    <product_code></product_code>
                                    <target_product></target_product>
                                    <reinvest></reinvest>
                                    <amt_unit_type></amt_unit_type>
                                    <amt_unit></amt_unit>
                                    <all_unit></all_unit>
                                    <from_date></from_date>
                                    <to_date></to_date>
                                    <periodicity></periodicity>
                                </childtrans>
                            </NMFIIService>'''

REQUEST_SYSTRXNREG = '''<NMFIIService>
                            <service_request>
                            <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                            <password>''' + NSE_NMF_PASSWORD + '''</password>
                            <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                            <iin></iin>
                            <trxn_type></trxn_type>
                            <dp_id></dp_id>
                            <euin_opted></euin_opted>
                            <euin></euin>
                            <sub_brok_arn></sub_brok_arn>
                            <trxn_acceptance></trxn_acceptance>
                            <acc_no></acc_no>
                            <bank></bank>
                            <branch></branch>
                            <acc_type></acc_type>
                            <micr_no></micr_no>
                            <ifsc_code></ifsc_code>
                            <debit_amt_type></debit_amt_type>
                            <umrn> </umrn>
                            <ach_amt></ach_amt>
                            <ach_fromdate></ach_fromdate>
                            <ach_enddate></ach_enddate>
                            <until_cancelled></until_cancelled>
                            <trans_count></trans_count>
                            </service_request>
                        </NMFIIService>'''

REQUEST_REDEEM_CHILDTXN = '''<NMFIIService>
                                <childtrans>
                                    <amc></amc>
                                    <folio></folio>
                                    <product_code></product_code>
                                    <amt_unit_type></amt_unit_type>
                                    <amt_unit></amt_unit>
                                    <all_units></all_units>
                                </childtrans>
                            </NMFIIService>'''

REQUEST_REDEEMTXN = '''<NMFIIService>
                            <service_request>
                            <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                            <password>''' + NSE_NMF_PASSWORD + '''</password>
                            <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                            <iin></iin>
                            <poa></poa>
                            <trxn_acceptance></trxn_acceptance>
                            <dp_id></dp_id>
                            <bank_name></bank_name>
                            <ac_no></ac_no>
                            <ifsc_code></ifsc_code>
                            <remarks></remarks>
                            <trans_count></trans_count>
                            </service_request>
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

REQUEST_CEASESIP = '''<NMFIIService>
                        <service_request>
                            <appln_id>''' + NSE_NMF_APPL_ID + '''</appln_id>
                            <password>''' + NSE_NMF_PASSWORD + '''</password>
                            <broker_code>''' + NSE_NMF_BROKER_CODE + '''</broker_code>
                            <iin></iin>
                            <trxn_no></trxn_no>
                            <cease_req_date></cease_req_date>
                            <initiated_by></initiated_by>
                            <nigo_remarks></nigo_remarks>
                        </service_request>
                    </NMFIIService>'''
