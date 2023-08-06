from django.conf.urls.defaults import patterns, url
from django.views.decorators.csrf import csrf_exempt

from djsocialtext.views import WebHookReceiver

urlpatterns = patterns('',
    url(r'^webhooks/$', csrf_exempt(WebHookReceiver.as_view()), name="djsocialtext_webhook_receiver"),
)
