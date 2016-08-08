"""nseapis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import nseapis
from . import views

urlpatterns = [
    url(r'^admin/',                     admin.site.urls                 ),
    url(r'^nse/create/customer/',       views.create_nse_customer       ),
    url(r'^nse/customer/iin/',          views.get_customer_iin          ),
    url(r'^nse/customer/iin/details/',  views.get_customer_iin_details  ),
    url(r'^nse/register/kyc/',          views.register_kyc              ),
    url(r'^nse/txn/purchase/',          views.txn_purchase              ),
    url(r'^nse/txn/redeem/',            views.txn_redeem                ),
    url(r'^nse/txn/switch/',            views.txn_switch                )
]