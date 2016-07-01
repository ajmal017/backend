from django.conf import settings

from oauth2_provider.models import Application

from profiles.models import User
from core.models import ExchangeRate, CachedData

import time


user = User.objects.create_superuser(email='admin@finaskus.com', password='admin@123')
time.sleep(1)

application = Application(client_id=settings.CLIENT_ID, user=user, client_type='confidential',
                          authorization_grant_type='password', client_secret=settings.CLIENT_SECRET, name='finaskus')
application.save()
time.sleep(1)

ExchangeRate.objects.get_or_create(key="exchange_rate", value="66")

# Creates a row to be updated using cron
CachedData.objects.create(key="most_popular_funds", value={})
