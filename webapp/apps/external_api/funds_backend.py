class BaseFundBackend(object):
    """
    Base class for fund backend implementations.
    Subclasses must at least overwrite get_data_points_for_funds(), get_dat_points_for_fund_data_points_change_monthly()
    and get_dat_points_for_fund_data_points_change_daily()
    """
    def __init__(self, **kwargs):
        pass

    def get_data_points_for_funds(self):
        """
        receive data for fund model
        """
        raise NotImplementedError

    def get_data_points_for_fund_data_points_change_monthly(self):
        """
        receive data for fund data points change monthly model
        :return:
        """
        raise NotImplementedError

    def get_data_points_for_fund_data_points_change_daily(self):
        """
        receive data for fund data points change daily model
        """
        raise NotImplementedError

    def get_data_points_for_equity(self):
        """
        receive data for equity model
        """
        raise NotImplementedError

    def get_data_points_for_debt(self):
        """
        receive data for debt model
        """
        raise NotImplementedError
