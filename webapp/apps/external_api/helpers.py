from external_api import models
import logging
from external_api.nse.nsebackend import NSEBackend
from external_api.bse.bsebackend import BSEBackend
 

def generate_logger_message(field, fund):
    """
    Generates string for debug logger
    :param field: the field which had a problem
    :param fund: the fund id which had a problem
    :return: a string in a specified format
    """
    return 'Something went wrong with ' + field + ' for fund with mstar id ' + fund['_id']


def calculate_beta(nav_funds, nav_benchmarks):
    """
    helper to calculate beta for funds whose betas are not provided by morning star
    :param nav_funds: nav of funds for last 36 months
    :param nav_benchmarks:nav of related benchmark for last 36 months
    :return:
    """
    nav_fund_difference, nav_benchmark_difference, squared_nav_benchmark_difference = 0.0, 0.0, 0.0
    product_of_diff = 0.0
    average_nav_funds = sum(nav_funds) / len(nav_funds)
    average_nav_benchmarks = sum(nav_benchmarks) / len(nav_benchmarks)
    min = nav_funds
    if len(nav_funds) > len(nav_benchmarks):
        min = nav_benchmarks
    for index in range(len(min)):
        nav_fund_difference = (nav_funds[index] - average_nav_funds)
        nav_benchmark_difference = (nav_benchmarks[index] - average_nav_benchmarks)
        product_of_diff += (nav_fund_difference * nav_benchmark_difference)
        squared_nav_benchmark_difference += pow(nav_benchmark_difference, 2)
    covariance = product_of_diff / (len(nav_funds) - 1)
    variance_benchmarks = squared_nav_benchmark_difference / (len(nav_benchmarks) - 1)
    return round(covariance / variance_benchmarks, 2)

class VendorHelper():
    activeVendor = None
    logger = logging.getLogger("django.error")
    
    def get_active_vendor(self):
        if not self.activeVendor:
            try:
                activeVendors = models.Vendor.objects.filter(active=True)
                if activeVendors and len(activeVendors) > 0:
                    self.activeVendor = activeVendors[0]
            except Exception as e:
                self.logger.error("Error getting active vendor:" + str(e))
                
        return self.activeVendor
    
    def get_backend_instance(self, vendor_name):
        if not vendor_name:
            active_vendor = self.get_active_vendor()
            if active_vendor:
                vendor_name = active_vendor.name
                
        if vendor_name == "NSE":
            return NSEBackend(vendor_name)
        
        if vendor_name == "BSE":
            return BSEBackend(vendor_name)
        
