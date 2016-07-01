# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^pay/', views.Pay.as_view(), name='pay'),

    # ======== DEPRECATED ==========
    # url(r"^get/checksum/$", views.TransactionString.as_view(), name='get-checksum')

]
