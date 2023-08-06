VERSION = (0, 2, 3, "")

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])


def get_api(**kwargs):
    """
    Get the Socialtext API client.

    :param api_cls: The API class to instantiate. Defaults to socialtext.Socialtext.
                    The provided class must accept the Socialtext URL, user, and user
                    password as positional arguments.
    :param url: The URL of the Socialtext appliance
    :param username: The username to use for authentication
    :param password: The password to use for authentication
    """
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from socialtext import Socialtext

    if 'api_cls' in kwargs:
        api_cls = kwargs['api_cls']
        kwargs.pop('api_cls')
    else:
        api_cls = Socialtext

    values = {
        "username": None,
        "password": None,
        "url": None
    }
    values.update(kwargs)


    # get values from settings.py
    kwarg_to_settings_mapping = {
        "url": "ST_URL",
        "username": "ST_USER",
        "password": "ST_PASSWORD"
    }

    for k,v in values.iteritems():
        # check if kwarg provided to method is None
        if v is None:
            # Check for value in django settings module
            settings_key = kwarg_to_settings_mapping.get(k, None)
            if hasattr(settings, settings_key):
                # override the None value in kwargs
                values[k] = getattr(settings, settings_key)

    return api_cls(**values)
