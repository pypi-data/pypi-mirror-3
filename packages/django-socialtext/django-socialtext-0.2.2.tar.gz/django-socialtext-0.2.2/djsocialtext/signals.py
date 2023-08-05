import django.dispatch

_base_signal = lambda: django.dispatch.Signal(providing_args=["webhook"])

webhook_all = _base_signal()

webhook_page_all = _base_signal()
webhook_page_delete = _base_signal()
webhook_page_update = _base_signal()
webhook_page_tag = _base_signal()
webhook_page_watch = _base_signal()
webhook_page_unwatch = _base_signal()

webhook_signal_all = _base_signal()
webhook_signal_create = _base_signal()

def always(webhook):
	return True

def is_action(webhook, action):
	return webhook["class"] == action

def OR(*l):
    # lets you run multiple permissions against a single state transition
    return lambda *args: any(f(*args) for f in l)

SIGNAL_CHOICES = [
	(lambda hook: True, webhook_all),
	(lambda hook: hook["class"].find("page.") == 0, webhook_page_all),
	(lambda hook: is_action(hook, "page.delete"), webhook_page_delete),
	(lambda hook: is_action(hook, "page.update"), webhook_page_update),
	(lambda hook: is_action(hook, "page.tag"), webhook_page_tag),
	(lambda hook: is_action(hook, "page.watch"), webhook_page_watch),
	(lambda hook: is_action(hook, "page.unwatch"), webhook_page_unwatch),

	(lambda hook: hook["class"].find("signal.") == 0, webhook_signal_all),
	(lambda hook: is_action(hook, "signal.create"), webhook_signal_create)
]

def send_for_webhook(sender, webhook):

	for choice in SIGNAL_CHOICES:
		func = choice[0]

		if func(webhook):
			choice[1].send(sender=sender, webhook=webhook)

