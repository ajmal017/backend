PROFILE_UPDATE_ERROR = "Error in updating the profile."
PROFILE_GET_ERROR = "Error in getting the profile."
NON_EXISTENT_USER_ERROR = "User does not exist."
NON_ACTIVE_USER_ERROR = "User is not active."
INCORRECT_EMAIL = "The email provided is not correct."
INCORRECT_SMS_CODE = "Incorrect OTP. Please re-enter valid OTP."
INCORRECT_OLD_PASSWORD = "The old password does not match your password. Please check it again."
PHONE_VERIFIED = "You phone number has been verified."
LOGIN_ERROR = "Incorrect password."
SIGNUP_ERROR = "Failed to register user."
PHONE_ALREADY_VERIFIED = "This user has already been verified!"
OTP = "Welcome to FinAskus. To complete signup," \
      " please use {} as one time password (OTP). Do not share this OTP with anyone for security reasons."

FORGOT_PASSWORD_OTP = "You have requested for a password change for your FinAskus account. " \
                      "For verification, please use {} as One Time Password (OTP). " \
                      "Do not share this OTP with anyone for security reasons."

RESET_PHONE_NUMBER_OTP = "You have requested for a phone number change for your FinAskus account." \
                         " For verification, please use {} as One Time Password (OTP). " \
                         "Do not share this OTP with anyone for security reasons."

RESET_EMAIL_SENT = "A password reset link has been sent to your registered Email ID."
VERIFY_EMAIL_SENT = "We've emailed you instructions for verifying your email," \
                    " if an account exists with the email you entered." \
                    " You should receive them shortly. If you don't receive an email," \
                    " please make sure you've entered the address you registered with, and check your spam folder."
VERIFY_SMS_SENT = "The OTP has been sent again."
VERIFY_SMS_NOT_SENT = "The OTP has not been sent."
EMAIL_VERIFIED = "Email verified and rendered to email_verified.html"
CODE_NOT_SAME_ERROR = "Code not same"
SITE_NAME = "Finaskus"
UNABLE_TO_RESET = "Unable to reset password."
UNABLE_TO_LOGIN = "Unable to login."
IDENTITY_IMAGE_SAVED = "Identity image saved"
USER_VIDEO_SAVED = "user video saved"
PINCODE_DOES_NOT_EXIST = "Pincode does not exist"
INCORRECT_PINCODE_SET = "Error in pincode, city and state combination"
PAN_IMAGE_SAVED = "Pan card image saved"
CONTACT_INFO_DOES_NOT_EXIST = "The requested contact info does not exist."
SUCCESS = "success"
MALFORMED = "Malformed request sent"
NON_EXISTENT_CONTACT_INFO_ERROR = "Contact info does not exist."
NON_EXISTENT_CONTACT_NOMINEE_ERROR = "Nominee info does not exist."
INVESTOR_INFO_INCOMPLETE = "Vault is incomplete."
NON_EXISTENT_APPOINTMENT_ERROR = "Appointment does not exist."
PHONE_NOT_VERIFIED = "Mobile number not verified. Please login using email and then verify mobile number in Settings."
EMAIL_NOT_VERIFIED = "Email not verified. Please login using your mobile number or verify email."
PHONE_AND_EMAIL_NOT_VERIFIED = "User does not exist. Please sign up and verify credentials."
USER_ALREADY_EXISTS = "User already exists. Please Login."
EMAIL_EXISTS = "User with same email already exist."
PHONE_EXISTS = "User with same phone already exist."
SIGNATURE_SAVED = "Signature is saved."
BANK_CHEQUE_SAVED = "Image of cheque is saved."
MESSAGE = 'message'
INVESTOR_ACCOUNT_NOT_PRESENT = 'Investor account details not present'
INVESTOR_DOES_NOT_EXIST = 'Investor does not exist.'

PRIVATE_SECTOR = 'PRI'
PROFESSIONAL = 'PRO'
BUSINESS = 'BUS'
HOUSEWIFE = 'HOU'
PUBLIC_SECTOR = 'PUB'
GOVERNMENT = 'GOV'
RETIRED = 'RET'
FOREX_DEALER = 'FOR'
AGRICULTURE = 'AGR'
STUDENT = 'STU'
OTHER = 'OTH'

LEVEL_0 = '0'
LEVEL_1 = '1'
LEVEL_2 = '2'
LEVEL_3 = '3'
LEVEL_4 = '4'
LEVEL_5 = '5'
LEVEL_6 = '6'

LOGIN_ERROR_0 = 0  # user serializer errors
LOGIN_ERROR_1 = 1  # user with the given email or phone does not exist.
LOGIN_ERROR_2 = 2  # both email and phone not verified hence not able to login.
LOGIN_ERROR_3 = 3  # phone_number is not verified.
LOGIN_ERROR_4 = 4  # email is not verified.
LOGIN_ERROR_5 = 5  # incorrect password entered.
LOGIN_ERROR_6 = 6  # non-active user.

SIGNUP_ERROR_0 = 0  # 000 - both email and phone are same as previously registered values + same password is used
#  + verified: please login.
SIGNUP_ERROR_1 = 1  # 001 - both same + same password + not verified: proceed with sign up.
SIGNUP_ERROR_2 = 2  # 010 - both same + different password + verified: user already exists please login.
SIGNUP_ERROR_3 = 3  # 011 - both different(both email and phone are different than the previously registered one.)
# : new user creation.
SIGNUP_ERROR_4 = 4  # 100 - only email matches: user with this email already exists
SIGNUP_ERROR_5 = 5  # 101 - only phone matches: user with this phone_number already exists
SIGNUP_ERROR_6 = 6  # 110 - both same + different password + not verified: update user's password and
#  ask them to verify.

DEFAULT_CONTACT_INFO = {
                        "communication_address": {},
                        "permanent_address": {},
                        "address_are_equal": None,
                        "address_proof_type": None,
                        "front_image": None,
                        "back_image": None
                        }

RESEND_MAIL_SUCCESS = 'Email sent successfully!'
RESEND_MAIL_FAILURE = "Email couldn't be sent!"
IFSC_CODE = 'ifsc_code'
USER = 'user'
INCORRECT_IFSC_CODE = 'IFSC code is incorrect'

USER_IMAGE_FIELD_LIST = ['is_bank_info', 'is_nominee_info', 'is_contact_info', 'is_investor_info', 'is_identity_info']
MALFORMED_REQUEST = "Malformed request is sent"
PASSWORD_CHANGED = "The password has been successfully changed."
EMAIL_PHONE_NOT_PROVIDED = 'Email or phone was not provided.'
EMAIL_NOT_PRESENT = 'Email is available'
EMAIL_ALREADY_PRESENT = 'Email is already registered.'
PHONE_NOT_PRESENT = 'Phone Number is available.'
PHONE_ALREADY_PRESENT = 'Phone Number already registered'
USER_WITH_EMAIL_NOT_PRESENT = 'User with given email is not present'
VERIFICATION_CODE_NOT_PRESENT = 'User did not requested for password change.'

DEFAULT_BANK_MANDATE_AMOUNT = 10000

