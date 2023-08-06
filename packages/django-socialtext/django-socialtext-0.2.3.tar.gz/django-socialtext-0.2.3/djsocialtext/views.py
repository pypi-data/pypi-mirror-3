from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson as json
from django.views import generic

from djsocialtext.signals import send_for_webhook

class WebHookReceiver(generic.View):
    def get(self, *args, **kwargs):
        return HttpResponse("Hello world!")

    def post(self, *args, **kwargs):
        if not "payload" in self.request.POST:
            raise HttpResponseBadRequest()
        
        payload = self.request.POST["payload"]

        webhooks = json.loads(payload)

        for webhook in webhooks:
            send_for_webhook(self, webhook)
            

        return HttpResponse("OK")
