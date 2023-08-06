from riak import RiakHttpTransport

__all__ = ['get_settings']

def get_default_settings():
    """
    @rtype: dict
    """
    return {
        'RIAK_DOC_DBS': {
            'DEFAULT': {
                'HOST': 'localhost',
                'PORT': 8098,
                'TRANSPORT': RiakHttpTransport
            },
        }
    }

try:
    from django.conf import settings

    def django_get_settings(settings):
        return getattr(settings, 'RIAK_DOC_DBS', default=get_default_settings())

    get_settings = django_get_settings

except ImportError, e:
    get_settings = get_default_settings