Components
================
Engage supports the automatic installation of optional
*components*. These components are complete services which typically
include operating sytem packages, python packages, configuration
scripts, and startup/shutdown management. The components currently
supported include:
 * ``redis`` - the `Redis key-value store <http://redis.io>`_
 * ``celery`` - `RabbitMQ message broker <http://www.rabbitmq.com>`_ accessed via `Celery <http://celeryproject.org>`_
 * ``memcached`` - `Memcached object cache <http://memcached.org>`_

Specifying Components
-------------------------
To specify one or more components, create a file
``engage_components.json`` under your project root directory. In the
:ref:`running_example`, this file goes under ``test_app_v1``. This
file should contain a JSON array with the names of your requested
components (redis, celery, memcached). For example, if you wish to
install celery and memcached, the file ``engage_components.json``
should contain the following::

    ["celery", "memcached"]

With this file added, you can now package your application and deploy
it as described in :doc:`deployment`. During its validation phase, the
packager will install any client-side python packages needed for the
associated components into the ``virtualenv`` that it creates. This will
prevent any imports of those packages in your settings file or
Django apps from failing during validation.

Using components
---------------------
Each component has a number of relevent configuration
variables. At deployment time, Engage will define additional settings in your settings
file to allow your application to make use of the components. We list
the settings defined for each component below.

**Celery/RabbitMQ**

The Celery/RabbitMQ settings are self-explanatory:
 * BROKER_HOST
 * BROKER_PORT
 * BROKER_USER
 * BROKER_PASSWORD
 * BROKER_VHOST
 * CELERY_RESULT_BACKEND

**Redis**

The Redis settings are self-explanatory:
 * REDIS_HOST
 * REDIS_PORT

**Memcached**

If ``memcached`` is enabled, Engage will add to your settings file both the
``CACHE_BACKEND`` setting (to work with the `Django 1.2 Cache Framework <https://docs.djangoproject.com/en/1.2/topics/cache>`_) and
the ``CACHES`` setting (to work with the `Django 1.3 Cache Framework <https://docs.djangoproject.com/en/1.3/topics/cache>`_).
