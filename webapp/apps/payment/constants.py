DISTRIBUTOR_ID = "ARN-108537"
MERCHANT_ID = "FINASKUS"
UNKNOWN = "NA"
DEFAULT_INVESTOR_TYPE = "RESIDENT"
BSE = "BSE"
LUMPSUM = "L"
LIQUID = "LIQUID"
NONLIQUID = "NONLIQUID"
MALFORMED_REQUEST = "Malformed request is sent"
ORDER_CREATION_FAILED = "Order creation failed. Please try again after sometime."
MESSAGE = 'message'
USER_BANK_DETAIL_NOT_PRESENT = 'user bank detail is not present'
USER_IFSC_CODE_INCORRECT = 'ifsc code in user bank details is incorrect'
USER_CANNOT_INVEST = 'You must be KRA verified and vault must be complete before investing.'
USER_KYC_CANNOT_GENERATE = "User's vault must be completed before generating this."
CANNOT_GENERATE_FILE = 'User must be KRA verified and vault must be complete before this action can be done.'

bank_product_id_map = {
    "ABHYUDAYA COOPERATIVE BANK LIMITED": ["", ""],
    "ABU DHABI COMMERCIAL BANK": ["", ""],
    "AHMEDABAD MERCANTILE COOPERATIVE BANK": ["", ""],
    "AKOLA JANATA COMMERCIAL COOPERATIVE BANK": ["", ""],
    "ALLAHABAD BANK": ["ALB", "DIRECT"],
    "ALMORA URBAN COOPERATIVE BANK LIMITED": ["", ""],
    "ANDHRA BANK": ["ADB", "DIRECT"],
    "ANDHRA BANK CORPORATE": ["", ""],
    "ANDHRA PRAGATHI GRAMEENA BANK": ["", ""],
    "APNA SAHAKARI BANK LIMITED": ["", ""],
    "AUSTRALIA AND NEW ZEALAND BANKING GROUP LIMITED": ["", ""],
    "AXIS BANK": ["UTI", "DIRECT"],
    "BANDHAN BANK LIMITED": ["", ""],
    "BANK INTERNASIONAL INDONESIA": ["", ""],
    "BANK OF AMERICA": ["", ""],
    "BANK OF BAHARAIN AND KUWAIT BSC": ["BBK", "DIRECT"],
    "BANK OF BARODA": ["BBR", "DIRECT"],
    "BANK OF BARODA CORPORATE": ["", ""],
    "BANK OF CEYLON": ["", ""],
    "BANK OF INDIA": ["", ""],
    "BANK OF MAHARASHTRA": ["BOM", "DIRECT"],
    "BANK OF TOKYO MITSUBISHI LIMITED": ["", ""],
    "BARCLAYS BANK": ["", ""],
    "BASSEIN CATHOLIC COOPERATIVE BANK LIMITED": ["", ""],
    "BHARAT COOPERATIVE BANK MUMBAI LIMITED": ["", ""],
    "BHARATIYA MAHILA BANK LIMITED": ["BMN", "DIRECT"],
    "B N P PARIBAS": ["", ""],
    "CANARA BANK": ["CNB", "DIRECT"],
    "CAPITAL LOCAL AREA BANK LIMITED": ["", ""],
    "CATHOLIC SYRIAN BANK LIMITED": ["CSB", "DIRECT"],
    "CENTRAL BANK OF INDIA": ["CBI", "DIRECT"],
    "CHINATRUST COMMERCIAL BANK LIMITED": ["", ""],
    "CITI BANK": ["", ""],
    "CITIZEN CREDIT COOPERATIVE BANK LIMITED": ["", ""],
    "CITY UNION BANK LIMITED": ["", ""],
    "COMMONWEALTH BANK OF AUSTRALIA": ["", ""],
    "CORPORATION BANK": ["CRP", "DIRECT"],
    "CREDIT AGRICOLE CORPORATE AND INVESTMENT BANK CALYON BANK": ["", ""],
    "CREDIT SUISEE AG": ["", ""],
    "DCB BANK LIMITED": ["DC2", "DIRECT"],
    "DCB CORPORATE NETBANKING": ["", ""],
    "DENA BANK": ["DEN", "DIRECT"],
    "DEPOSIT INSURANCE AND CREDIT GUARANTEE CORPORATION": ["", ""],
    "DEUSTCHE BANK": ["DBK", "DIRECT"],
    "DEVELOPMENT BANK OF SINGAPORE": ["", ""],
    "DHANALAKSHMI BANK": ["DLB", "DIRECT"],
    "DOHA BANK QSC": ["", ""],
    "DOMBIVLI NAGARI SAHAKARI BANK LIMITED": ["", ""],
    "EXPORT IMPORT BANK OF INDIA": ["", ""],
    "FEDERAL BANK": ["FBK", "DIRECT"],
    "FEDERAL BANK SCAN&PAY": ["", ""],
    "FIRSTRAND BANK LIMITED": ["", ""],
    "G P PARSIK BANK": ["", ""],
    "HDFC BANK": ["HDF", "DIRECT"],
    "HSBC BANK": ["", ""],
    "ICICI BANK LIMITED": ["ICI", "DIRECT"],
    "IDBI BANK": ["IDB", "DIRECT"],
    "IDFC BANK LIMITED": ["", ""],
    "INDIAN BANK": ["INB", "DIRECT"],
    "INDIAN OVERSEAS BANK": ["IOB", "DIRECT"],
    "INDUSIND BANK": ["IDS", "DIRECT"],
    "INDUSTRIAL AND COMMERCIAL BANK OF CHINA LIMITED": ["", ""],
    "INDUSTRIAL BANK OF KOREA": ["", ""],
    "ING VYSYA BANK": ["", ""],
    "JALGAON JANATA SAHAKARI BANK LIMITED": ["", ""],
    "JAMMU AND KASHMIR BANK LIMITED": ["JKB", "DIRECT"],
    "JANAKALYAN SAHAKARI BANK LIMITED": ["", ""],
    "JANASEVA SAHAKARI BANK BORIVLI LIMITED": ["", ""],
    "JANASEVA SAHAKARI BANK LIMITED": ["", ""],
    "JANATA SAHAKARI BANK LIMITED": ["JSB", "DIRECT"],
    "JP MORGAN BANK": ["", ""],
    "KALLAPPANNA AWADE ICHALKARANJI JANATA SAHAKARI BANK LIMITED": ["", ""],
    "KALUPUR COMMERCIAL COOPERATIVE BANK": ["", ""],
    "KALYAN JANATA SAHAKARI BANK": ["", ""],
    "KAPOL COOPERATIVE BANK LIMITED": ["", ""],
    "KARNATAKA BANK LIMITED": ["KBL", "DIRECT"],
    "KARNATAKA VIKAS GRAMEENA BANK": ["", ""],
    "KARUR VYSYA BANK": ["KVB", "DIRECT"],
    "KEB Hana Bank": ["", ""],
    "KERALA GRAMIN BANK": ["", ""],
    "KOTAK MAHINDRA BANK LIMITED": ["162", "DIRECT"],
    "LAXMI VILAS BANK": ["LVR", "DIRECT"],
    "LAXMI VILAS BANK CORPORATE": ["", ""],
    "MAHANAGAR COOPERATIVE BANK": ["", ""],
    "MAHARASHTRA STATE COOPERATIVE BANK": ["", ""],
    "MASHREQBANK PSC": ["", ""],
    "MIZUHO CORPORATE BANK LIMITED": ["", ""],
    "NAGAR URBAN CO OPERATIVE BANK": ["", ""],
    "NAGPUR NAGARIK SAHAKARI BANK LIMITED": ["", ""],
    "NATIONAL AUSTRALIA BANK LIMITED": ["", ""],
    "NATIONAL BANK OF ABU DHABI PJSC": ["", ""],
    "NEW INDIA COOPERATIVE BANK LIMITED": ["", ""],
    "NKGSB COOPERATIVE BANK LIMITED": ["NKB", "DIRECT"],
    "NUTAN NAGARIK SAHAKARI BANK LIMITED": ["", ""],
    "ORIENTAL BANK OF COMMERCE": ["OBC", "DIRECT"],
    "PRAGATHI KRISHNA GRAMIN BANK": ["", ""],
    "PRATHAMA BANK": ["", ""],
    "PRIME COOPERATIVE BANK LIMITED": ["", ""],
    "PUNJAB AND MAHARSHTRA COOPERATIVE BANK": ["PMC", "DIRECT"],
    "PUNJAB AND SIND BANK": ["PSB", "DIRECT"],
    "PUNJAB NATIONAL BANK": ["PNB", "DIRECT"],
    "CORPORATE PUNJAB NATIONAL BANK": ["", ""],
    "RABOBANK INTERNATIONAL": ["", ""],
    "RAJGURUNAGAR SAHAKARI BANK LIMITED": ["", ""],
    "RAJKOT NAGRIK SAHAKARI BANK LIMITED": ["", ""],
    "RBL Bank Limited": ["RTN", "DIRECT"],
    "RESERVE BANK OF INDIA": ["", ""],
    "SAHEBRAO DESHMUKH COOPERATIVE BANK LIMITED": ["", ""],
    "SARASWAT COOPERATIVE BANK LIMITED": ["SWB", "DIRECT"],
    "SBER BANK": ["", ""],
    "SBM BANK MAURITIUS LIMITED": ["", ""],
    "SHIKSHAK SAHAKARI BANK LIMITED": ["", ""],
    "SHINHAN BANK": ["", ""],
    "SHRI CHHATRAPATI RAJASHRI SHAHU URBAN COOPERATIVE BANK LIMITED": ["", ""],
    "SOCIETE GENERALE": ["", ""],
    "SOLAPUR JANATA SAHAKARI BANK LIMITED": ["", ""],
    "SOUTH INDIAN BANK": ["SIB", "DIRECT"],
    "STANDARD CHARTERED BANK": ["SCB", "DIRECT"],
    "STATE BANK OF BIKANER AND JAIPUR": ["SBJ", "DIRECT"],
    "STATE BANK OF HYDERABAD": ["SBH", "DIRECT"],
    "STATE BANK OF INDIA": ["SBI", "DIRECT"],
    "STATE BANK OF MYSORE": ["SBM", "DIRECT"],
    "STATE BANK OF PATIALA": ["SBP", "DIRECT"],
    "STATE BANK OF TRAVANCORE": ["SBT", "DIRECT"],
    "SUMITOMO MITSUI BANKING CORPORATION": ["", ""],
    "SURAT NATIONAL COOPERATIVE BANK LIMITED": ["", ""],
    "SUTEX COOPERATIVE BANK LIMITED": ["", ""],
    "SYNDICATE BANK": ["SYD", "DIRECT"],
    "TAMILNAD MERCANTILE BANK LIMITED": ["TMB", "DIRECT"],
    "THE AKOLA DISTRICT CENTRAL COOPERATIVE BANK": ["", ""],
    "THE ANDHRA PRADESH STATE COOPERATIVE BANK LIMITED": ["", ""],
    "THE A.P. MAHESH COOPERATIVE URBAN BANK LIMITED": ["", ""],
    "THE BANK OF NOVA SCOTIA": ["", ""],
    "THE COSMOS CO OPERATIVE BANK LIMITED": ["COB", "DIRECT"],
    "THE DELHI STATE COOPERATIVE BANK LIMITED": ["", ""],
    "THE GADCHIROLI DISTRICT CENTRAL COOPERATIVE BANK LIMITED": ["", ""],
    "THE GREATER BOMBAY COOPERATIVE BANK LIMITED": ["", ""],
    "THE GUJARAT STATE COOPERATIVE BANK LIMITED": ["", ""],
    "THE HASTI COOP BANK LTD": ["", ""],
    "THE JALGAON PEOPELS COOPERATIVE BANK LIMITED": ["", ""],
    "THE KANGRA CENTRAL COOPERATIVE BANK LIMITED": ["", ""],
    "THE KANGRA COOPERATIVE BANK LIMITED": ["", ""],
    "THE KARAD URBAN COOPERATIVE BANK LIMITED": ["", ""],
    "THE KARANATAKA STATE COOPERATIVE APEX BANK LIMITED": ["", ""],
    "THE KURMANCHAL NAGAR SAHAKARI BANK LIMITED": ["", ""],
    "THE MEHSANA URBAN COOPERATIVE BANK": ["", ""],
    "THE MUMBAI DISTRICT CENTRAL COOPERATIVE BANK LIMITED": ["", ""],
    "THE MUNICIPAL COOPERATIVE BANK LIMITED": ["", ""],
    "THE NAINITAL BANK LIMITED": ["", ""],
    "THE NASIK MERCHANTS COOPERATIVE BANK LIMITED": ["", ""],
    "THE PANDHARPUR URBAN CO OP. BANK LTD. PANDHARPUR": ["", ""],
    "THE RAJASTHAN STATE COOPERATIVE BANK LIMITED": ["", ""],
    "THE ROYAL BANK OF SCOTLAND N V": ["RBS", "DIRECT"],
    "THE SEVA VIKAS COOPERATIVE BANK LIMITED": ["", ""],
    "THE SHAMRAO VITHAL COOPERATIVE BANK": ["SVC", "DIRECT"],
    "THE SURAT DISTRICT COOPERATIVE BANK LIMITED": ["", ""],
    "THE SURATH PEOPLES COOPERATIVE BANK LIMITED": ["", ""],
    "THE TAMIL NADU STATE APEX COOPERATIVE BANK": ["TNC", "DIRECT"],
    "THE THANE BHARAT SAHAKARI BANK LIMITED": ["", ""],
    "THE THANE DISTRICT CENTRAL COOPERATIVE BANK LIMITED": ["", ""],
    "THE VARACHHA COOPERATIVE BANK LIMITED": ["", ""],
    "THE VISHWESHWAR SAHAKARI BANK LIMITED": ["", ""],
    "THE WEST BENGAL STATE COOPERATIVE BANK": ["", ""],
    "THE ZOROASTRIAN COOPERATIVE BANK LIMITED": ["", ""],
    "TJSB SAHAKARI BANK LTD": ["TJB", "DIRECT"],
    "TUMKUR GRAIN MERCHANTS COOPERATIVE BANK LIMITED": ["", ""],
    "UCO BANK": ["UCO", "DIRECT"],
    "UNION BANK OF INDIA": ["UBI", "DIRECT"],
    "UNITED BANK OF INDIA": ["UNI", "DIRECT"],
    "UNITED OVERSEAS BANK LIMITED": ["", ""],
    "VASAI VIKAS SAHAKARI BANK LIMITED": ["", ""],
    "VIJAYA BANK": ["VJB", "DIRECT"],
    "WESTPAC BANKING CORPORATION": ["", ""],
    "WOORI BANK": ["", ""],
    "YES BANK": ["YBK", "DIRECT"],
    "ZILA SAHAKRI BANK LIMITED GHAZIABAD": ["", ""],
}

UNAVAILABE_BANK = "The bank set in Bank information section of vault is not supported by us right now. Please change it."
