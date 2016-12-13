import logging
from django.db.models import F
from core import constants


class RiskProfileHelper(object):
    
    error_logger = logging.getLogger('django.error')
    defaut_risk_score = 7.0
    risk_profile_weights = {constants.RISK_PROFILE_A: 1, constants.RISK_PROFILE_B: 2,
                           constants.RISK_PROFILE_C: 3, constants.RISK_PROFILE_D: 4,
                           constants.RISK_PROFILE_E: 5,}

    tenure_weights = [{"tenure": 2, "weight": -5},
                       {"tenure": 4, "weight": -3},
                       {"tenure": 6, "weight": 0},
                       {"tenure": 9, "weight": 1},
                       {"tenure": 14, "weight": 2},
                       {"tenure": 100, "weight": 3}
                       ]
    
    weight_to_risk_cat = [constants.RISK_PROFILE_ONLY_DEBT, constants.RISK_PROFILE_A, constants.RISK_PROFILE_B,
                          constants.RISK_PROFILE_C, constants.RISK_PROFILE_D,
                          constants.RISK_PROFILE_E, constants.RISK_PROFILE_ONLY_EQUITY]
    
    weight_to_risk_cat_len = len(weight_to_risk_cat)
    
    def __init__(self, user):
        super(RiskProfileHelper, self).__init__()
        self.user = user
        
    def get_risk_profile(self):
        """
        """
        if not self.user:
            return None
        
        risk_profile = None
        risk_score = self.user.risk_score
        if risk_score is None:
            risk_score = self.defaut_risk_score
            
        if risk_score <= 4:
            risk_profile = constants.RISK_PROFILE_A
        elif risk_score <= 6:
            risk_profile = constants.RISK_PROFILE_B
        elif risk_score <= 7.5:
            risk_profile = constants.RISK_PROFILE_C
        elif risk_score <= 8.5:
            risk_profile = constants.RISK_PROFILE_D
        else:
            risk_profile = constants.RISK_PROFILE_E

        return risk_profile
            
    def compute_risk_profile(self, tenure):
        if not self.user:
            return None

        risk_profile = self.get_risk_profile()
        risk_profile_code = self.risk_profile_weights[risk_profile]
        
        tenure_code = 0
        for w in self.tenure_weights:
            if tenure <= w["tenure"]:
                tenure_code = w["weight"]
                break
                 
        net_code = risk_profile_code + tenure_code

        computed_risk_category = constants.RISK_PROFILE_ONLY_EQUITY
        for code in range(self.weight_to_risk_cat_len):
            if net_code <= code:
                computed_risk_category = self.weight_to_risk_cat[code]
                break
            
        return computed_risk_category
    