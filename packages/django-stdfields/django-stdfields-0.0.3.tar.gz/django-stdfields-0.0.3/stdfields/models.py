# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str


class Enumeration(object):
    """
    Simple enumeration object - subclasses should implement ``all``,
    mapping keys to values.
    """

    @classmethod
    def as_dict(cls):
        """
        Returns the key-label pairs of the enumeration.
        """
        return dict((k, v) for (k, v) in cls.all())

    @classmethod
    def as_display(cls, key):
        """Returns the label or display value of the key."""
        return cls.as_dict().get(key, None)

    @classmethod
    def all(cls):
        """
        Returns all key-label pairs as a list of tuples.

        Useful to pass on to a field as the possible choices. Will be used
        internally by the customer enum fields. Should be *implemented* by 
        subclasses.
        """
        return []

    @classmethod
    def max_length(cls):
        """
        Calculates the maximum length of the key.

        You can set the ``max_length`` value of a ``CharField`` or
        ``EnumCharField`` to the result of this method. That way South will be
        able to pick up any changes to the maximum key length automatically.
        """
        keys = [smart_str(x[0]) for x in cls.all()]
        value = max(keys, key=lambda x: len(x))
        return 1 if not value else len(value)
