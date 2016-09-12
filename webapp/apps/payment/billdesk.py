from django.conf import settings

from . import utils, models


def verify_billdesk_checksum(string):
    """
    :param string:
    :return: Boolean True if checksum match else false

    STEPS

    1)   This checksum value will be the last token in the  response message
    2)   You need to park this BillDesk computed checksum value in a local variable
    3)   You then need to remove the BillDesk computed checksum value and the preceding pipe (|), thereby this
         makes the response string as the original response string for which BillDesk has computed the checksum value.
    4)   You now need to compute the checksum value for this original response string and compare with what was
         shared by BillDesk
    """

    response_checksum = string.split("|")[-1:][0]
    string_to_be_hashed = "|".join(string.split("|")[:-1])
    hash_generated = utils.get_billdesk_checksum(string_to_be_hashed, settings.BILLDESK_SECRET_KEY)
    return True if hash_generated == response_checksum else False


def update_transaction_failure(order_number, ref_no, txn_amount, auth_status, msg, txn_time):
    """
    :return: Changes the status of the transaction to failure code(ie 2)
    """
    txn = models.Transaction.objects.get(additional_info_1=order_number, txn_amount=txn_amount,
                                         txn_status=models.Transaction.Status.Pending.value)
    if txn.txn_status == models.Transaction.Status.Pending.value:
        txn.txn_status = models.Transaction.Status.Failure.value
        txn.auth_status = auth_status
        txn.txn_reference_no = ref_no
        txn.txn_time = txn_time
        txn.response_string = {"string": msg}
        txn.save()
    return txn


def update_transaction_success(order_number, ref_no, txn_amount, auth_status, msg, txn_time):
    """
    :return:  Changes the status of the transaction to failure code(ie 1)
    """
    if auth_status == "0300":
        txn = models.Transaction.objects.get(additional_info_1=order_number, txn_amount=txn_amount,
                                             txn_status=models.Transaction.Status.Pending.value)
        if txn.txn_status == models.Transaction.Status.Pending.value:
            txn.txn_status = models.Transaction.Status.Success.value
            txn.auth_status = auth_status
            txn.txn_reference_no = ref_no
            txn.txn_time = txn_time
            txn.response_string = {"string": msg}
            txn.save()
            return txn

    else:
        txn = update_transaction_failure(order_number, ref_no, txn_amount, auth_status, msg, txn_time)
        return txn


def parse_billdesk_response(string):
    """

    :param string: string to be parsed on basis of pipe
    :return: following
    order_id: parsed_string[1]
    ref_no: parsed_string[2]
    txn_amount: parsed_string[4]
    auth_status: parsed_string[14]
    """
    parsed_string = string.split('|')
    return parsed_string[1], parsed_string[2], parsed_string[4], parsed_string[14], parsed_string[13]



