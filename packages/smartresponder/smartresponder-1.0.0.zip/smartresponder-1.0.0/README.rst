=========
smartresponder
=========

This is a smartresponder (aka smartresponder.ru)
python API wrapper. The goal is to support all API methods (current and future)
that can be accessed from server.

Installation
============

::

    $ pip install smartresponder

Usage
=====

::

    >>> import smartresponder
    >>> api = smartresponder.API('my_api_id', 'my_api_secret')
    >>> subscriber = api.subscribers.list(id='39715947')['list']['elements'][0]
    >>> print subscriber['email']
    test@test.ru

All API methods that can be called from server should be supported.

See http://goo.gl/DrmQU for detailed API help.