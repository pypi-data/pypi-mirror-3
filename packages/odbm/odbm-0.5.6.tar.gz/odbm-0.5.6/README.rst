odbm
====

Links
-----

- repository: https://bitbucket.org/imbolc/odbm/
- russian docs: http://pysi.org/lab/odbm/

Installation
------------

    $  pip install odbm

Usage
-----

::

    >>> from datetime import datetime
    >>> import odbm
    
    >>> class User(odbm.Model):
    ...     username = odbm.UnicodeProperty(primary_key=True)
    ...     friends  = odbm.Property(default=[], key='f')
    ...     created  = odbm.DateTimeProperty(key='c')
    ...
    ...     __backend__ = staticmethod(lambda: dict())
    
    >>> User(
    ...     username = 'foo',
    ...     friends  = ['bar', 'baz'],
    ...     created = datetime.now(),
    ... ).save()
    >>> User(username='bar', created = datetime.now()).save()
    >>> User(username='baz', created = datetime.now()).save()
    
    >>> User.get('foo').friends
    ['bar', 'baz']
    
    >>> [u.username for u in User.find(
    ...     filter  = lambda u: not u.friends,
    ...     order   = lambda x: x.created)]
    [u'bar', u'baz']

    >>> User.count()
    3
    >>> User.count(lambda u: 'baz' in u.friends)
    1
    >>> User.find_one().delete()
    >>> User.count()
    2