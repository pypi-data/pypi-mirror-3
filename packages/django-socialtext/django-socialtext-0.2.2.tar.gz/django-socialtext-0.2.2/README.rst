django-socialtext
=================

A django application that helps integrate Socialtext with your project.

This application will help you interact with the Socialtext ReST API and
receive webhooks from your Socialtext appliance.

Installation
------------

1. Install django-socialtext on your PYTHONPATH::

	pip install django-socialtext

	# or

	easy_install django-socialtext

2. Add 'djsocialtext' to your project's INSTALLED_APPS
3. Configure the djsocialtext settings::

	ST_URL = "https://st.example.com" # URL for your ST appliance

	ST_USER = "joeuser" # your ST username

	ST_PASSWORD = "joepassword" # your ST password


Usage
-----

Djsocialtext helps you interact with the ReST API by providing a shortcut method
to instantiate a python-socialtext__ API client using your project's settings::

	from djsocialtext import get_api

	api = get_api()

	api.workspaces.list()
	[<Workspace: blogs>, <Workspace: marketing>]

__ https://github.com/hanover/python-socialtext

Contributing
------------

Development takes place on GitHub__. You can file pull requests and issue tickets there.

__ https://github.com/hanover/django-socialtext
