#-*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [

    url(r"^verifiable/pincode/$", views.VerifiablePincode.as_view(), name='verifiable-pincode'),
    url(r'^bank/info/get/', views.BankInfoGet.as_view(), name='bank-info-get'),
    url(r"^verifiable/kyc/$", views.KycApi.as_view(), name='kyc_get_status'),
    url(r'^generate/investor/info/pdf/$', views.GenerateInvestorPdf.as_view(), name='generate_investor_pdf'),
    url(r'^generate/kyc/info/pdf/$', views.GenerateKycPdf.as_view(), name='generate_kyc_pdf'),
    url(r'^generate/bse/investor/tiff/$', views.GenerateAOFTiff.as_view(), name='generate_bse_investor_tiff'),
    url(r'^upload/investor/tiff/$', views.UploadAOFTiff.as_view(), name='upload_investor_tiff'),
    url(r'^generate/bank/mandate/pdf/$', views.GenerateMandatePdf.as_view(), name='generate_bank_mandate_pdf'),
    url(r'^generate/bse/order/pipe/$', views.GenerateBseOrderPipe.as_view(), name='generate_bse_order_pipe'),
    url(r'^generate/bse/redeem/pipe/$', views.GenerateBseRedeemPipe.as_view(), name='generate_bse_redeem_pipe'),
    url(r'^generate/xsip/registration/$', views.GenerateXsipRegistration.as_view(), name='generate_xsip_Registration'),
    url(r'^generate/bank/mandate/$', views.GenerateBankMandateRegistration.as_view(), name='generate_bank_mandate'),
    url(r'^nse/order/$', views.NseOrder.as_view(), name='nse_order'),
    url(r'^sip/cancellation/admin/$', views.SipCancellation_admin.as_view(), name='sip-cancellation'),
    url(r'^generate/user/csv/$', views.GenerateUserCsv.as_view(), name='generate_user_csv')
]
