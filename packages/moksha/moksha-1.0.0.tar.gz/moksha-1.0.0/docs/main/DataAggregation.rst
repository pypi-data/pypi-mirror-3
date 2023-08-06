================
Data Aggregation
================

Moksha provides many ways to acquire data in an efficient manner.

Messaging layer
---------------

Moksha can communicate with various message brokers, using the `AMQP
<http://amqp.org>`_, `STOMP <http://stomp.codehaus.org/Protocol>`_,
and/or `0mq <http://www.zeromq.org/>`_
protocols.  It also provides a simple API for producing and consuming messages,
as well as allowing widgets to subscribe to live message streams within the
users web browser.

Caching layer
-------------

A flexible caching layer is available to all Moksha widgets and applications.
This middleware is setup by TurboGears2, and trivializes the act of caching
expensive operations.

Moksha also provides recipies for integrating with nginx & memcached.

Moksha Feed API
---------------

Moksha provides a powerful Feed widget that automatically handles fetching,
parsing, and caching arbitrary feeds in an efficient, scalable manner.
