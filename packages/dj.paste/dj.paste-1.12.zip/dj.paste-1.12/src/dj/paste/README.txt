django factory
-----------------------------------------

Checking that everything is in place::

    >>> resp = app.get('/')
    >>> 'first django' in resp.body.lower()
    True


