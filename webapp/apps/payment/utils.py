import hmac
import hashlib


def date_time_format(date_obj, txn_amt):
    """
    :return:formatted date in yyyymmddhhmmss format
    """
    date = date_obj.strftime("%Y%m%d%H%M%S")
    return date+"-"+str(txn_amt)+"-0.00"


def get_billdesk_checksum(string, secret_key):
    """

    :param string: String to be hashed
    :param secret_key: A secret used for hashing
    :return: hashed string
    """
    bytes_string = string.encode('utf-8')
    bytes_secret_key = secret_key.encode('utf-8')
    sign = hmac.new(bytes_secret_key, bytes_string, digestmod=hashlib.sha256).hexdigest()
    return sign.upper()

