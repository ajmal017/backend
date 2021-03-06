from django.conf import settings

from webapp.apps.external_api import constants
from webapp.apps import code_generator
from core import models as core_models
from collections import OrderedDict

import logging
from datetime import date
import os

logger = logging.getLogger("default")

class BillDeskPayment(object):
        
    def createOutputFile(self, name):
        base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
        output_path = base_dir + '/webapp/static/'
        outfile = open(output_path + name, "w")
        return outfile, output_path + name

    def generateBSEUploadFile(self, txns):
        from payment import models as payment_models

        dt_today_str = date.today().strftime("%d%m%Y")
        out_filename = 'FW_FUN_' + dt_today_str + '.txt'
        out_file, out_filepath = self.createOutputFile(out_filename)
        
        missing_order_ids = []
        for pay in txns:
            if pay.txn_status == payment_models.Transaction.Status.Success:
                order_details = core_models.OrderDetail.objects.filter(transaction=pay)
            
                for order in order_details:
                    for fund_order_item in order.fund_order_items.all():
                        if int(fund_order_item.order_amount) > 0:
                            if not fund_order_item.bse_transaction_id:
                                missing_order_ids.append(fund_order_item)
                            else:
                                bse_order_dict = OrderedDict([('ORDER DATE', fund_order_item.modified_at.strftime('%d/%m/%Y')), 
                                                           ('Order ID', str(fund_order_item.bse_transaction_id)),
                                                           ('Client Code', str(pay.user.finaskus_id)),
                                                           ('Order Val AMOUNT', str(fund_order_item.order_amount))])
                                out_file.write("|".join(bse_order_dict.values()))
                                out_file.write("\r")
                                bse_order_dict.clear()
        
        out_file.close()
        if len(missing_order_ids) > 0:
            return missing_order_ids, "MISSING_BSE_ORDER_ID"
        
        return "webapp/static/" + os.path.basename(out_filepath), None
        
    def generateBSEUploadFileForDate(self, paydate):
        from payment import models as payment_models
        
        self.paydate = paydate
        payments = payment_models.Transaction.objects.filter(txn_time__month=self.pay_date.month, txn_time__day=self.pay_date.day,
                                            txn_time__year = self.pay_date.year, txn_status=payment_models.Transaction.Status.Success)
        
        return self.generateBSEUploadFile(payments)


# transaction = Payment(constants.GET_PASSWORD_URL)
# passkey = code_generator(8)
# transaction.get_encrypted_password(settings.BSE_DEMO_USERID, settings.BSE_DEMO_MEMBERID, settings.BSE_DEMO_PASSWORD, passkey)
