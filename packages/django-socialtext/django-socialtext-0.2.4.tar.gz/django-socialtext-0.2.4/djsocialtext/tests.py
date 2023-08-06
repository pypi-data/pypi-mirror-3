from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.test import TestCase
from django.test.client import Client

from djsocialtext import get_api
from djsocialtext import signals

class DummyConfig(object):
    """
    A dummy config class
    """
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            setattr(self, k, v)


class DummyApi(object):
    """
    A dummy API class
    """
    def __init__(self, **kwargs):
        self.config = DummyConfig(**kwargs)


class ApiTestCase(TestCase):

    def test_get_api(self):
        api = get_api()

        # the API client should have the proper settings
        self.assertEqual(settings.ST_URL, api.config.url)
        self.assertEqual(settings.ST_USER, api.config.username)
        self.assertEqual(settings.ST_PASSWORD, api.config.password)
        
    def test_get_injected_api(self):
        # test that the method will use an injected class
        api = get_api(api_cls=DummyApi)
        self.assertTrue(isinstance(api, DummyApi))
        
    def test_override_credentials(self):
        api = get_api(url="https://dummy.com", username="dummy", password="foo")
        self.assertEqual("https://dummy.com", api.config.url)
        self.assertEqual("dummy", api.config.username)
        self.assertEqual("foo", api.config.password)

class WebHookReceiverTest(TestCase):

    urls = "djsocialtext.test_urls"

    def setUp(self):
        self.client = Client()
        self.url = reverse("djsocialtext_webhook_receiver")
    
    def test_get(self):
        """
        Tests that the view returns 200 for GETs
        """
        self.assertEqual(200, self.client.get(self.url).status_code)

    def test_post_with_minimal_payload(self):
        """
        Tests that the view returns 200 for a POST with a payload POST
        """
        json_data = [
            {
                "class": "hello.world"
            }
        ]
         
        post_data = {
            "payload": json.dumps(json_data)
        }
        self.assertEqual(200, self.client.post(self.url, data=post_data).status_code)


signal_output = []

def webhook_all_test(signal, sender, **kwargs):
    signal_output.append("webhook_all signal")

def webhook_page_all_test(signal, sender, **kwargs):
    signal_output.append("webhook_page_all signal")

def webhook_page_delete_test(signal, sender, **kwargs):
    signal_output.append("webhook_page_delete signal")

def webhook_signal_all_test(signal, sender, **kwargs):
    signal_output.append("webhook_signal_all signal")

def webhook_signal_create_test(signal, sender, **kwargs):
    signal_output.append("webhook_signal_create signal")

class SignalsTest(TestCase):
    def setUp(self):
        # Save up the number of connected signals so that we can check at the end
        # that all the signals we register get properly unregistered
        self.pre_signals = (len(signals.webhook_page_all.receivers),
                        len(signals.webhook_signal_all.receivers))

        signals.webhook_all.connect(webhook_all_test)
        
        signals.webhook_page_all.connect(webhook_page_all_test)
        signals.webhook_page_delete.connect(webhook_page_delete_test)
        
        signals.webhook_signal_all.connect(webhook_signal_all_test)
        signals.webhook_signal_create.connect(webhook_signal_create_test)

    def tearDown(self):
        signals.webhook_page_all.disconnect(webhook_page_all_test)
        signals.webhook_signal_all.disconnect(webhook_signal_all_test)

        # Check that all our signals got disconnected properly.
        post_signals = (len(signals.webhook_page_all.receivers),
                        len(signals.webhook_signal_all.receivers))
        
        self.assertEqual(self.pre_signals, post_signals)


    def get_signal_output(self, fn, *args, **kwargs):
        # Flush any existing signal output
        global signal_output
        signal_output = []
        fn(*args, **kwargs)
        return signal_output

    def _create_webhook(self, action):
        return {
            "class": action
        }

    def test_webhook_page_all(self):
        webhook = self._create_webhook("page.foo")
        self.assertEqual(self.get_signal_output(signals.send_for_webhook, self, webhook), [
            "webhook_all signal",
            "webhook_page_all signal"
        ])

    def test_webhook_page_delete(self):
        webhook = self._create_webhook("page.delete")
        self.assertEqual(self.get_signal_output(signals.send_for_webhook, self, webhook), [
            "webhook_all signal",
            "webhook_page_all signal", # this should raise webhook_page_all too
            "webhook_page_delete signal"
        ])
    

    def test_webhook_signal_all(self):
        webhook = self._create_webhook("signal.foo")
        self.assertEqual(self.get_signal_output(signals.send_for_webhook, self, webhook), [
            "webhook_all signal",
            "webhook_signal_all signal"
        ])

    def test_webhook_signal_create(self):
        webhook = self._create_webhook("signal.create")
        self.assertEqual(self.get_signal_output(signals.send_for_webhook, self, webhook), [
            "webhook_all signal",
            "webhook_signal_all signal", # this should raise webhook_signal_all too
            "webhook_signal_create signal"
        ])
