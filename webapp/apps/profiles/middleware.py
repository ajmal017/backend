from django.contrib import auth
from django.conf import settings

from datetime import datetime, timedelta


class AutoLogout:
    """
    This middleware makes sure that admin inactivity after specified period of time, ensures logout.
    Also no matter active or inactive, the admin is forcefully logged out after the compulsory timeout period
    """
    def process_request(self, request):
        """
        On each admin request the the time for inactivity and also total time is tested to
        check if it has crossed the specified time period.

        :param request: The request contains the user type. If the user is admin the timers are tested.
        :return:
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated():
            # Can't log out if not logged in
            return None

        try:
            if request.user.is_admin:
                # only for admin user.

                # check if logged in for the first time.
                if 'latest_login' in request.session:
                    # if not first time then check if inactivity has been for more than INACTIVE TIMEOUT value.
                    if datetime.now() - request.session['latest_login'] > timedelta(0, settings.INACTIVE_LOGOUT_DELAY * 60, 0):
                        # if inactive for more than timeout value, then log the user out.
                        auth.logout(request)

                        # clear the session values.
                        del request.session['latest_login']
                        del request.session['compulsory_log_out']
                        return None
                    else:
                        request.session['latest_login'] = datetime.now()  # still active. So reset the
                        # Inactive session timer.

                        # the user has been active for more than the COMPULSORY TIMEOUT value.
                        if datetime.now() - request.session['compulsory_log_out'] > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                            # log him out and clear the session values.
                            auth.logout(request)
                            del request.session['latest_login']
                            del request.session['compulsory_log_out']
                        return None
                else:
                    # first time login. Intialize the timer values in the session.
                    # both latest_touch and compulsory_log_out are initialized here.
                    request.session['latest_login'] = datetime.now()
                    request.session['compulsory_log_out'] = datetime.now()

        except KeyError:
            return None
