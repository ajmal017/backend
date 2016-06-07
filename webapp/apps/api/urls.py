#-*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url, include

urlpatterns = [
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^user/", include('profiles.urls', namespace='profiles_urls')),
    url(r"^core/", include('core.urls', namespace='core_urls')),
    url(r"^payment/", include('payment.urls', namespace='payment_urls')),
    url(r"^open/", include('external_api.urls', namespace='external_api_urls'))
]
