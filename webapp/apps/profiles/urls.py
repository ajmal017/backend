# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^info/$", views.UserInfo.as_view(), name='user-info'),
    url(r"^login/$", views.Login.as_view(), name='login-user'),
    url(r'^profile/completeness/', views.ProfileCompleteness.as_view(), name='profile-completeness'),
    url(r"^register/$", views.Register.as_view(), name='register-user'),
    url(r"^reset/password/$", views.ResetPassword.as_view(), name='reset-password'),
    url(r"^change/password/$", views.ChangePassword.as_view(), name='change-password'),
    url(r'^verify/phone/$', views.VerifyPhone.as_view(), name="phone_activation"),
    url(r"^resend/verify/email/$", views.ResendVerifyEmail.as_view(), name='resend-verify-email'),
    url(r"^resend/verify/phone/$", views.ResendVerifyPhone.as_view(), name='resend-verify-phone'),
    url(r"^resend/forgot/password/$", views.ResendForgotPassword.as_view(), name='resend-forgot-password'),
    url(r"^resend/verify/email/admin/$", views.ResendVerifyEmailAdmin.as_view(), name='resend-verify-email-admin'),
    url(r"^email/status/$", views.EmailStatus.as_view(), name='email-status'),
    url(r"^change/email/$", views.ChangeEmail.as_view(), name='change-email'),
    url(r"^verify/confirm/(?P<token>[A-Z0-9]{50})/$", views.CheckEmailCode.as_view(), name='check-email-code'),
    url(r"^save/image/$", views.SaveImage.as_view(), name='save-image'),
    url(r"^pincode/autocomplete/$", views.PincodeInfo.as_view(), name='pincode-autocomplete'),
    url(r"^investor/info/get/$", views.InvestorInfo.as_view(), name='investor-info-get'),
    url(r"^investor/info/add/skip/$", views.InvestorInfo.as_view(), name='investor-info-add-skip'),
    url(r"^investor/info/add/$", views.InvestorInfo.as_view(), name='investor-info-add'),
    url(r"^contact/info/get/$", views.ContactInfo.as_view(), name='investor-contact-info-get'),
    url(r"^contact/info/add/skip/$", views.ContactInfoSkip.as_view(), name='investor-contact-info-add-skip'),
    url(r"^contact/info/add/$", views.ContactInfo.as_view(), name='investor-contact-info-add'),
    url(r"^identity/info/get/$", views.IdentityInfo.as_view(), name='identity-info-get'),
    url(r"^identity/info/add/skip/$", views.IdentityInfoSkip.as_view(), name='identity-info-add-skip'),
    url(r"^identity/info/add/$", views.IdentityInfo.as_view(), name='identity-info-add'),
    url(r"^nominee/info/add/$", views.NomineeInfo.as_view(), name='investor-nominee-info-add'),
    url(r"^nominee/info/get/$", views.NomineeInfo.as_view(), name='investor-nominee-info-get'),
    url(r"^signature/get/$", views.GetSignature.as_view(), name='signature-get'),
    url(r"^is_complete/get/$", views.IsCompleteView.as_view(), name='is-complete-get'),
    url(r"^appointment/get/$", views.AppointmentSchedule.as_view(), name='appointment-get'),
    url(r"^appointment/add/$", views.AppointmentSchedule.as_view(),
        name='appointment-add'),
    url(r"^is_complete/update/$", views.IsCompleteView.as_view(), name='is-complete-update'),
    # url(r"^phone/delete/$", views.DeletePhonenumber.as_view(), name='is-complete-update'),
    url(r"^process/set/$", views.SetProcessChoice.as_view(), name='process-set'),
    url(r'^investor/account/info/get/$', views.InvestorAccountInfoGet.as_view(), name='investor-account-info-get'),
    url(r'^investor/account/info/post/$', views.InvestorAccountInfoPost.as_view(), name='investor-account-post'),
    url(r'^check/email_or_phone/$', views.CheckEmailPhone.as_view(), name='check-email-or-phone'),
    url(r'^verify/forgot/password/otp/$', views.VerifyForgotPasswordOTP.as_view(), name='verify-forgot-password-otp'),
    url(r'^change/phone/number/$', views.ChangePhoneNumber.as_view(), name='change-phone-number'),
    url(r'^confirm/change/phone/number/$', views.ConfirmChangeInPhoneNumber.as_view(), name='confirm-change-in-phone-number'),
    url(r'^video/upload/$', views.VideoUpload.as_view(), name='user-video-upload'),
    url(r'^video/get/$', views.VideoGet.as_view(), name='user-video-get'),
    url(r'^signature/get/$', views.Signature.as_view(), name='user-signature-get'),
]
