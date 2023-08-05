"""
Module level configuration for Mongo Alchemy

"""

from mongoalchemy.util import UNSET, classproperty


__all__ = ['configure']


# This is pre-populated with our defaults
CONFIG = {
    'namespace':'global',
    'extra_fields':'error',
    'eager_validation':False,
    'strict':True,
    'allow_none':False,
    'required':True,
    'counter_collection':'_counters',
    }


def configure(*args, **kwargs):
    """
    Sets all the options via a handy helper.

    :param str namespace: default namespace to use
    :param str extra_fields: how to handle extra fields passed to a \
            :class:`~mongoalchemy.document.Document` constructor
    :param bool eager_validation: whether to validate at assignment time
    :param bool strict: whether to try trivial type coercion
    :param bool allow_none: whether to allow None as a value for fields
    :param bool required: whether a fields must be present on a document
    :param str counter_collection: name of the counter collection to use

    """
    if len(args) > 1:
        raise TypeError("Too many positional arguments. Expected 0 or 1, got %s." % len(args))

    options = {}
    if args:
        options = args[0]
        if not isinstance(options, dict):
            raise TypeError("First argument must be a dict instance.")

    options.update(kwargs)
    invalid = [k for k in options if k not in CONFIG]
    if invalid:
        raise ValueError("Got invalid option keys: %s" % invalid)

    CONFIG.update(options)


def config_property(name):
    """ Helper to create fail-through config properties.

        :param name: name of the config_* property
    """
    return ConfigProperty(name)


class ConfigProperty(object):
    """ ConfigProperty attribute.

        Returns the value set on the property itself if it is set,
        otherwise returns the value set on `self.parent`, if set, and if
        neither of those, returns the value stored in :data:`CONFIG`.

    """
    def __init__(self, name):
        self.cls_name = 'config_' + name
        self.name = name

    def __get__(self, instance, owner):
        cls_name = self.cls_name
        name = self.name
        if instance:
            self = instance
        else:
            self = owner

        if hasattr(self, '_config') and name in self._config:
            return self._config[name]

        parent = getattr(self, 'parent', None)
        if parent:
            val = getattr(parent, cls_name, UNSET)
            if val != UNSET:
                return val

        return CONFIG[name]

    def __set__(self, instance, value):
        name = self.name

        if value != UNSET:
            if not hasattr(instance, '_config'):
                instance._config = {}
            instance._config[name] = value

