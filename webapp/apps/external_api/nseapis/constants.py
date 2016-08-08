NSE_NMF_API_URL     = "http://124.124.236.198/NMFIITrxnService/NMFTrxnService/"
NSE_NMF_APPL_ID     = "MFS108537"
NSE_NMF_PASSWORD    = "finaskus1@"
NSE_NMF_BROKER_CODE = "ARN-108537"

NMF_METHOD_CREATECUSTOMER           = "CREATECUSTOMER"
NMF_METHOD_IINDETAILS               = "IINDETAILS"
NMF_METHOD_PURCHASETRXN             = "PURCHASETRXN"
NMF_METHOD_REDEEMTRXN               = "REDEEMTRXN"
NMF_METHOD_SWITCHTRXN               = "SWITCHTRXN"
NMF_METHOD_SYSTRXNREG               = "SYSTRXNREG"
NMF_METHOD_CEASESIP                 = "CEASESIP"
NMF_METHOD_TRXNREVERSEFEED          = "TRXNREVERSEFEED"
NMF_METHOD_ALLIINDETAILS            = "ALLIINDETAILS"
NMF_METHOD_FATCAKYCUBOREG           = "FATCAKYCUBOREG"
NMF_METHOD_EDITCUSTOMER             = "EDITCUSTOMER"
NMF_METHOD_IINMODIFICATIONSTATUS    = "IINMODIFICATIONSTATUS"
NMF_METHOD_ACHMANDATEREGISTRATIONS  = "ACHMANDATEREGISTRATIONS"
NMF_METHOD_ACHMANDATEREPORT         = "ACHMANDATEREPORT"
NMF_METHOD_SYSCEASEREPORT           = "SYSCEASEREPORT"
NMF_METHOD_SYSREGISTRATIONSREPORT   = "SYSREGISTRATIONSREPORT"
NMF_METHOD_GETIIN                   = "GETIIN"

REQUEST_CREATECUSTOMER = '''<NMFIIService>
                    <service_request>
                        <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                        <password>'''+NSE_NMF_PASSWORD+'''</password>
                        <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                        <title>Mr.</title>
                        <inv_name>anil jadhav</inv_name>
                        <pan>BJKPM3516R</pan>
                        <valid_pan>Y</valid_pan>
                        <exemption>N</exemption>
                        <exempt_category></exempt_category>
                        <exempt_ref_no></exempt_ref_no>
                        <dob>02-jan-1989</dob>
                        <hold_nature>SI</hold_nature>
                        <tax_status>06</tax_status>
                        <kyc>Y</kyc>
                        <occupation>1A</occupation>
                        <mfu_can></mfu_can>
                        <dp_id></dp_id>
                        <father_name></father_name>
                        <mother_name></mother_name>
                        <trxn_acceptance>ph</trxn_acceptance>
                        <addr1>xxx</addr1>
                        <addr2></addr2>
                        <addr3></addr3>
                        <city>Ahmedabad</city>
                        <state>GU</state>
                        <pincode>384250</pincode>
                        <country>IND</country>
                        <mobile_no>8975641235</mobile_no>
                        <res_phone></res_phone>
                        <off_phone></off_phone>
                        <res_fax></res_fax>
                        <off_fax></off_fax>
                        <email>test@gmail.com</email>
                        <nri_addr1></nri_addr1>
                        <nri_addr2></nri_addr2>
                        <nri_addr3></nri_addr3>
                        <nri_city></nri_city>
                        <nri_state></nri_state>
                        <nri_pincode></nri_pincode>
                        <nri_country></nri_country>
                        <bank_name>ICICI</bank_name>
                        <acc_no>037010100256352</acc_no>
                        <acc_type>SB</acc_type>
                        <ifsc_code>ICIC0001878</ifsc_code>
                        <branch_name></branch_name>
                        <branch_addr1>yamunanagar,pune</branch_addr1>
                        <branch_addr2></branch_addr2>
                        <branch_addr3></branch_addr3>
                        <branch_city>yamunanagar</branch_city>
                        <branch_pincode>411045</branch_pincode>
                        <branch_country>IND</branch_country>
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
                        <no_of_nominee>0</no_of_nominee>
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
                    <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                    <password>'''+NSE_NMF_PASSWORD+'''</password>
                    <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                    <tax_status>01</tax_status>
                    <hold_nature>SI</hold_nature>
                    <exempt_flag>N</exempt_flag>
                    <fh_pan>APOPS7121K</fh_pan>
                    <jh1_exempt_flag>N</jh1_exempt_flag>
                    <jh1_pan></jh1_pan>
                    <jh2_exempt_flag>N</jh2_exempt_flag>
                    <jh2_pan></jh2_pan>
                    <guardian_pan></guardian_pan>
                    </service_request>
                </NMFIIService>'''

REQUEST_IINDETAILS = '''<NMFIIService>
                        <service_request>
                        <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                        <password>'''+NSE_NMF_PASSWORD+'''</password>
                        <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                        <iin>5011000029</iin>
                        </service_request>
                    </NMFIIService>'''

REQUEST_FATCAKYCUBOREG = '''<NMFIIService>
                            <service_request>
                            <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                            <password>'''+NSE_NMF_PASSWORD+'''</password>
                            <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                            <pan>ABCDE0113K</pan>
                            <tax_status>01</tax_status>
                            <investor_name>Karthik</investor_name>
                            <chkExempIndValid>N</chkExempIndValid>
                            <editor_id>KGNANA</editor_id>
                            <KYC_availability>Y</KYC_availability>
                            <FATCA_availability>Y</FATCA_availability>
                            <UBO_availability>Y</UBO_availability>
                            <ubo_applicable_count>2</ubo_applicable_count>
                            <KYC>
                                <app_income_code>34</app_income_code>
                                <net_worth>5000</net_worth>
                                <net_worth_date>31-Jul-2015</net_worth_date>
                                <pep>Y</pep>
                                <occ_code>1</occ_code>
                                <source_wealth>03</source_wealth>
                                <corp_servs>01</corp_servs>
                                <aadhaar_rp>234534535341234</aadhaar_rp>
                            </KYC>
                            <Fatca>
                                <dob>31-Jul-1987</dob>
                                <addr_type>2</addr_type>
                                <data_src>E</data_src>
                                <log_name>Karthikeyanm@sterlingsoftware.co.in</log_name>
                                <country_of_birth>IND</country_of_birth>
                                <place_birth>PO</place_birth>
                                <tax_residency>N</tax_residency>
                                <country_tax_residency1>IND</country_tax_residency1>
                                <tax_payer_identityno1>PYBQI9229X</tax_payer_identityno1>
                                <id1_type>C</id1_type>
                                <country_tax_residency2></country_tax_residency2>
                                <tax_payer_identityno2></tax_payer_identityno2>
                                <id2_type></id2_type>
                                <country_tax_residency3></country_tax_residency3>
                                <tax_payer_identityno3></tax_payer_identityno3>
                                <id3_type></id3_type>
                                <country_tax_residency4></country_tax_residency4>
                                <tax_payer_identityno4></tax_payer_identityno4>
                                <id4_type></id4_type>
                                <ffi_drnfe></ffi_drnfe>
                                <nffe_catg></nffe_catg>
                                <nature_bus></nature_bus>
                                <act_nfe_subcat></act_nfe_subcat>
                                <stock_exchange></stock_exchange>
                                <listed_company></listed_company>
                                <us_person>N</us_person>
                                <exemp_code></exemp_code>
                                <giin_applicable></giin_applicable>
                                <giin></giin>
                                <giin_exem_cat></giin_exem_cat>
                                <sponcer_entity></sponcer_entity>
                                <giin_not_app></giin_not_app/>
                                <fatca_dec_received>Y</fatca_dec_received>
                            </Fatca>
                            <ubo>
                                <ubo_add1>df</ubo_add1>
                                <ubo_add2>ddd</ubo_add2>
                                <ubo_add3>dd</ubo_add3>
                                <ubo_applicable>Y</ubo_applicable>
                                <ubo_master_codes>C04</ubo_master_codes>
                                <ubo_pan_no>THTHT1234P</ubo_pan_no>
                                <ubo_name>BDDD</ubo_name>
                                <ubo_country_tax_residency>IND</ubo_country_tax_residency>
                                <ubo_cob>TN</ubo_cob>
                                <ubo_cocn>IND</ubo_cocn>
                                <ubo_country>IND</ubo_country>
                                <ubo_declartion>YES</ubo_declartion>
                                <ubo_dob>14-Jan-1988</ubo_dob>
                                <ubo_father_nam>JDFD</ubo_father_nam>
                                <ubo_gender>M</ubo_gender>
                                <ubo_holding_perc>100</ubo_holding_perc>
                                <ubo_occ_code>3D</ubo_occ_code>
                                <ubo_tel_no>5151515</ubo_tel_no>
                                <ubo_mobile>9876543121</ubo_mobile>
                                <ubo_pincode>123123</ubo_pincode>
                                <ubo_city>SDF</ubo_city>
                                <ubo_state>SDF</ubo_state>
                                <ubo_add_type>1</ubo_add_type>
                                <ubo_id_type>C</ubo_id_type>
                                <ubo_tin_no>SADFD6265D</ubo_tin_no>
                            </ubo>
                        </service_request>
                    </NMFIIService'''
                    
REQUEST_TXN_PURCHASE = '''<NMFIIService>
                            <service_request>
                            <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                            <password>'''+NSE_NMF_PASSWORD+'''</password>
                            <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                            <iin>5011006336</iin>
                            <sub_trxn_type>N</sub_trxn_type>
                            <poa>N</poa>
                            <trxn_acceptance>OL</trxn_acceptance>
                            <demat_user>N</demat_user>
                            <dp_id></dp_id>
                            <bank>AXIS</bank>
                            <ac_no>037010100256352</ac_no>
                            <ifsc_code>UTIB0000037</ifsc_code>
                            <sub_broker_arn_code></sub_broker_arn_code>
                            <sub_broker_code></sub_broker_code>
                            <euin_opted>N</euin_opted>
                            <euin></euin>
                            <trxn_execution></trxn_execution>
                            <remarks></remarks>
                            <payment_mode>OL</payment_mode>
                            <billdesk_bank>AXIS</billdesk_bank>
                            <instrm_bank></instrm_bank>
                            <instrm_ac_no></instrm_ac_no>
                            <instrm_no></instrm_no>
                            <instrm_amount>3232</instrm_amount>
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
                            <nominee_flag>N</nominee_flag>
                            <no_of_nominee>0</no_of_nominee>
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
                            <Return_paymnt_flag>Y</Return_paymnt_flag>
                            <Client_callback_url> Provide your Webpage / API URL </Client_callback_url>
                            <trans_count>1</trans_count>
                            </service_request>
                            <childtrans>
                                <amc>T</amc>
                                <folio></folio>
                                <product_code>SIP3G</product_code>
                                <reinvest>N</reinvest>
                                <amount>10000</amount>
                                <sip_from_date></sip_from_date>
                                <sip_end_date></sip_end_date>
                                <sip_freq></sip_freq>
                                <sip_amount></sip_amount>
                                <sip_period_day></sip_period_day>
                            </childtrans>
                        </NMFIIService>'''
REQUEST_TXN_REDEEM   = '''<NMFIIService>
                        <service_request>
                        <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                        <password>'''+NSE_NMF_PASSWORD+'''</password>
                        <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                        <iin>5011006336</iin>
                        <poa>N</poa>
                        <trxn_acceptance>OL</trxn_acceptance>
                        <dp_id></dp_id>
                        <acc_no>037010100256352</acc_no>
                        <bank_name>AXIS</bank_name>
                        <ifsc_code>UTIB0000037</ifsc_code>
                        <remarks>test</remarks>
                        <trans_count>1</trans_count>
                        </service_request>
                        <childtrans>
                            <amc>T</amc>
                            <folio>5145607</folio>
                            <product_code>SIP3G</product_code>
                            <amt_unit_type>Amount</amt_unit_type>
                            <amt_unit>1000</amt_unit>
                            <all_units>N</all_units>
                        </childtrans>
                    </NMFIIService>'''
REQUEST_TXN_SWITCH   = '''<NMFIIService>
                        <service_request>
                        <appln_id>'''+NSE_NMF_APPL_ID+'''</appln_id>
                        <password>'''+NSE_NMF_PASSWORD+'''</password>
                        <broker_code>'''+NSE_NMF_BROKER_CODE+'''</broker_code>
                        <iin>5011000029</iin>
                        <poa>Y</poa>
                        <trxn_acceptance>OL</trxn_acceptance>
                        <dp_id>2345678901122222</dp_id>
                        <sub_broker_arn_code>0441124578212</sub_broker_arn_code>
                        <sub_broker_code>ARN-0145</sub_broker_code>
                        <euin_opted>Y / N</euin_opted>
                        <euin>E123456</euin>
                        <trxn_execution></trxn_execution>
                        <remarks>test</remarks>
                        <trans_count></trans_count>
                        </service_request>
                        <childtrans>
                            <amc>D</amc>
                            <folio>5145607</folio>
                            <source_product_code>BFD</source_product_code>
                            <target_product_code>BFD</target_product_code>
                            <reinvest>Y</reinvest>
                            <amt_unit_type>Amount / Unit</amt_unit_type>
                            <amt_unit>1000</amt_unit>
                            <all_units>Y/N</all_units>
                        </childtrans>
                    </NMFIIService>'''