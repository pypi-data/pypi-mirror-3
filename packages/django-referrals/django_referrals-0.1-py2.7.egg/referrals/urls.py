from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = patterns('referrals.views',
    url(r'^refer/(?P<unique_key>[A-Za-z0-9_-]+)/$', 'refer', name='referral_refer'),
    url(r'^my-referrals/$', TemplateView.as_view(template_name='referrals/mine.html'), name='referral_mine'),
)
