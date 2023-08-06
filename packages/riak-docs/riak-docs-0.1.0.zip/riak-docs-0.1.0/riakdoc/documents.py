from riak import RiakHttpTransport, RiakClient
from abc import ABCMeta, abstractmethod

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'
__all__ = ['BaseRiakDocument']

class BaseRiakDocument(object):
    clients = {}
    using = None
    __metaclass__ = ABCMeta

    def __init__(self, key, obj=None, d=None, using=None, noclobber=True):
        """
        Create a basic Riak model.
        Arguments:
        @param key: The key to store/retrieve from Riak.
        @type key: str
        @param obj: A seed object to use for this model.
        @type obj: riak.riak_object.RiakObject
        @param d: A seed dictionary to use.
        @type d: dict
        @param using: Riak client
        @type using: riak.RiakClient
        @param noclobber: Whether or not to accept both a `d` and a `obj` with data.
        @type noclobber: bool
        """
        self.key = key
#        self.lock = AccessLock('{bucket}-{key}'.format(bucket=self.bucket, key=key))
        if not obj:
            obj = self.get_bucket(using=using).get(self.key)
            obj.set_content_type('application/json')
        self._obj = obj

        if d:
            if self._obj.exists() and self._obj.get_data() and noclobber:
                raise Exception('No clobber set but data and Riak object passed.')
            self.data = d
            self._obj.set_data(d)
        else:
            if self._obj.exists():
                self.data = obj.get_data()
            else:
                self.data = self.initialize_data()


    @classmethod
    def get_bucket_name(cls):
        """
        Return the name of the bucket.

        This should be an abstract class method, but we don't have that capability in my version of ABC.

        @rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_or_create_client(cls, using=None):
        """
        Returns a new instance of a riak.RiakClient based on the name and the project settings.
        """
        from riakdoc.settings import get_settings
        using = using or 'DEFAULT'
        if not using in cls.clients:
            try:
                settings = get_settings()['RIAK_DOC_DBS'][using]
            except KeyError:
                raise Exception('Improperly configured riakdoc database configuration for {0}'.format(using))
            else:
                cls.clients[using] = RiakClient(
                    host=settings.get('HOST', 'localhost'),
                    port=settings.get('PORT', 8098),
                    prefix=settings.get('PREFIX', 'riak'),
                    mapred_prefix=settings.get('MAPRED_PREFIX', 'mapred'),
                    transport_class=settings.get('TRANSPORT', RiakHttpTransport),
                    solr_transport_class=settings.get('SOLR_TRANSPORT', None)
                )
        return cls.clients[using]

    def get_client(self, using=None):
        """
        Return a `riak.RiakClient` instance.
        @param using: The key of the database from config to use (defaults to "default")
        @type using: str
        @rtype: riak.RiakClient
        """
        return self.get_or_create_client(using or self.using)

    @classmethod
    def get_if_exists(cls, key, using=None):
        riak_obj = cls.get_or_create_client(using=using).bucket(cls.get_bucket_name()).get(key)
        if riak_obj.exists():
            return cls(key, obj=riak_obj)
        else:
            return None

    @classmethod
    def get_bucket(cls, using=None):
        try:
            return cls._bucket
        except AttributeError:
            cls._bucket = cls.get_or_create_client(using=using).bucket(cls.get_bucket_name())
            return cls._bucket

    @abstractmethod
    def initialize_data(self):
        """
        Called when the object is created without existing in Riak, must return the data this object should have.
        """
        pass

    def pre_save(self):
        """Called right before saving to Riak."""
        pass

    def _set_object(self, obj):
        """
        set the Riak object.
        """
        self._obj = obj
        if obj.exists() and obj.get_data():
            self.data = obj.get_data()

    def save(self):
        self.pre_save()
        self._obj.set_data(self.data)
        self._obj.store()

    def delete(self):
        self._obj.delete()