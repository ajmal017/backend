"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from oauth2_provider import models as oauth_models

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from core import views
from profiles import views as profile_views
from django.views.generic import TemplateView

handler404 = 'core.views.my_custom_page_not_found_view'
handler500 = 'core.views.server_error'

urlpatterns = [
    # url(r'^grappelli/', include('grappelli.urls')),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        profile_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', profile_views.password_reset_complete, name='password_reset_complete'),
    url(r'^5a91a426e461/474a/admin/', include(admin.site.urls)),
    url(r"^v1.0/", include("api.urls", namespace='api_urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url('', include('django.contrib.auth.urls')),
    url(r"^$", views.index, name='index'),
    url(r"^privacy/$", views.privacy, name='privacy'),
    url(r"^terms/$", views.terms, name='terms'),
    url(r"^disclaimer/$", views.disclaimer, name='disclaimer'),
    url(r'^robots.txt', views.robots, name='robots'),
    url(r'^sitemap.xml', views.sitemap, name='sitemap'),
    url(r'^mutual-fund-scheme-related-documents', views.blank, name='blank'),
    url(r'^faq', views.faq, name='faq'),
    url(r'^index-new', views.indexnew, name='indexnew'),
    url(r'^mutual-fund-primer', views.mfprimer, name='mfprimer'),
    url(r'^mutual-fund-basics', views.mfbasics, name='mfbasics'),
    url(r'^retirement-planning', views.retirementplanning, name='retirementplanning'),
    url(r'^why-invest-in-mutual-funds', views.whymf, name='whymf'),
    url(r'^debt-funds-risk-free', views.debtfundsrisk, name='debtfundsrisk'),
    url(r'^a-sip-in-time-saves-nine', views.sipintime, name='sipintime'),
    url(r'^aboutus', views.aboutus, name='aboutus'),
    url(r'^mutual-fund-articles', views.mfarticles, name='mfarticles'),
    url(r'^blog', views.blog, name='blog'),
    url(r'^google59199aa04156c0bc.html$', TemplateView.as_view(template_name='google59199aa04156c0bc.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.unregister(oauth_models.AccessToken)
admin.site.unregister(oauth_models.Grant)
admin.site.unregister(oauth_models.RefreshToken)
admin.site.unregister(oauth_models.Application)
