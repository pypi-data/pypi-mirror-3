from django.conf import settings

__all__ = []

_DEFAULTS = {
    'CAS_TICKET_EXPIRATION': 5, # In minutes
    'CAS_CUSTOM_ATTRIBUTES_CALLBACK': None,
    'CAS_CUSTOM_ATTRIBUTES_FORMATER': 'cas_provider.attribute_formatters.jasig',
    'CAS_AUTO_REDIRECT_AFTER_LOGOUT': False,
}

for key, value in _DEFAULTS.iteritems():
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    except ImportError:
        pass
