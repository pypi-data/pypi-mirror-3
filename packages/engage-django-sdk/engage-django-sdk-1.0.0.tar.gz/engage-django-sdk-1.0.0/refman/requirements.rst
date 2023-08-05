Application Requirements
========================
The Engage Django SDK currently supports applications that run on
Django 1.3.

.. _file_layout:

File Layout
-----------
Engage expects all the files of your Django project to be under one directory
(we'll call this the *project root directory*). This includes
application code, static files, etc. The directory containing your
Django settings module will be added to your ``PYTHONPATH`` on the
deployed system(s).  In our :ref:`running_example`, the project
root directory is ``test_app_v1``, since all application files are under
that directory. If the Django settings module is ``test_app.settings``,
then the ``test_app_v1`` directory will be added to ``PYTHONPATH``
on the deployed server. 

If you provide a fully qualified name for
your settings module (e.g. ``test_app.settings``), Engage will add the
directory containing your settings file (e.g. ``test_app_v1/test_app``
in our example) to your ``PYTHONPATH`` as well. This is to handle any
implicit assumptions in your application due to running the
development server from that directory.

Any extra Python packages that you want
to include with your packaged application should be added under the
same directory as your django settings module tree. Continuing with
our  example, let's say that we want to use code from the ``utils``
package in our application. Since the ``utils`` directory is at the
same level as the settings module tree (under ``test_app_v1``), we can import files in this
directory as follows::

  import utils.fileutils
  import utils.misc

The django settings module name, location of extra Python packages,
and your python imports must all be consistent. In our example, if we
tell the validator that the Django settings module is ``settings``,
rather than ``test_app.settings``, the ``PYTHONPATH`` will be set to
``test_app_v1/test_app``. This will cause imports of
``utils.fileutils`` and ``utils.misc`` to fail.

Archive Files
~~~~~~~~~~~~~~~~
As we'll see in :doc:`deployment`, you can also provide an archive
file (in gzipped tar or zip format) containing your application to the
SDK, as long as the directory structure when extracted matches this
layout.


Application Dependencies
------------------------
You may also have third-party Python packages  that you wish to include
in your application. You may package them directly with your
application as described above. If the packages are registered on the
Python Package Index (http://pypi.python.org) or are available on a
public source control repository, you can also list them in a
requirements.txt file. These packages are then installed during the
deployment process as prerequisites to your application. The
requirements.txt file, if provided, should go directly under your
project root directory. The ``engage-django`` packager will
actually simulate this process on your desktop to catch potential
issues with missing packages.

Python packages referenced in the requirements.txt file
are installed using pip (http://www.pip-installer.org). See
http://www.pip-installer.org/en/latest/requirement-format.html for
details on the requirements.txt file format. Here is an example
requirements.txt file::

  django-classy-tags>=0.3.3
  django-sekizai>=0.4.2
  pil
  django-cms

You do not have to include the ``Django`` and ``South`` packages in
your requirements file, as they will be automatically installed by
Engage. We recommend *not* specifying particular versions of these two
packages, as Engage will pre-install versions tested
with the rest of the infrastructure.

Django Components
----------------------------
Engage also supports the specification of complete components to be
included with your Django install. Examples include Celery/RabbitMQ,
Memcached, and Redis. See :doc:`components` for details.


Django Settings
-----------------
For most applications, you can just use your existing ``settings.py`` file, as long
as it does not contain any absolute file path references. Certain settings will
be overridden by Engage (e.g. the database configuration) to match the desired
server configuration. For a description of Django settings and configuration in
general see http://docs.djangoproject.com/en/1.3/topics/settings/.

When deploying your application, Engage configures its settings as follows:

#. Your settings file is located using the Django settings module name
   provided when you packaged your application (described in
   :ref:`application_packaging`). The module tree containing your
   application can start at your project root or can be a subdirectory.
#. A new Python file is created in the same directory as your settings
   file called ``engage_settings.py``. This contains settings values
   provided by Engage (based on your desired
   configuration and the details of the system that has been provisioned for
   you).
#. A file called ``deployed_settings.py`` file is created. This file
   imports the your settings module and then overrides specific
   settings using values from engage_settings. The
   ``DJANGO_SETTING_MODULE`` environment variable is set to the
   ``deployed_settings`` module when running your application.


The following Django settings are overridden by Engage:

* ADMINS (provided by the user when Deploying their application)
* DATABASES (a new database will be created for the application)
* TIME_ZONE (provided by the user when deploying their application)
* SECRET_KEY (this will be randomly generated)
* LOGGING, LOGGING_CONFIG - these are new settings which appear in
  Django 1.3. Engage defines these settings to help configure its
  logging (see :ref:`logging`)

If you really want to provide your own value for one of these settings, define
the setting in your settings file and also define the variable
``<setting_name>_OVERRIDE`` (e.g. ``ADMINS_OVERRIDE``). This will
cause Engage to override its chosen value for the setting and use your value. Of course,
depending on the setting, this may cause problems at deployment time (e.g.
changing the default database may cause your deployment to fail).

Additional Configuration Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``engage_settings`` module defines a number of additional settings which may be
useful to your application:

* ``ENGAGE_APP_FILES_BASE`` - this is the full path to directory above
  your project root directory on the deployed system
* ``ENGAGE_WEBSERVER_HOSTNAME`` - the hostname of the public webserver for your
  deployed application
* ``ENGAGE_WEBSERVER_PORT`` - the TCP port of the public webserver for your
  deployed application
* ``ENGAGE_LOG_DIRECTORY`` - path to directory on deployed system where logfiles
  will be placed
* ``ENGAGE_LOG_FILE`` - path to logfile which is setup by Engage when starting your
  application (see :ref:`logging`)

Of course, since the ``engage_settings.py`` file is generated for you by Engage,
it is not available in your development environment. A simple workaround for
your settings.py file is to try importing the module and, if the import fails,
assign default values to those settings. For example::

    try:
        from engage_settings import ENGAGE_WEBSERVER_HOSTNAME, ENGAGE_WEBSERVER_PORT
    except ImportError:
        ENGAGE_WEBSERVER_HOSTNAME = 'localhost'
        ENGAGE_WEBSERVER_PORT = '8080'

Settings Involving File Paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The location of your deployed application on the deployed server's filesystem
is subject to change. Thus, you should not hard-code any absolute file paths in
your Django settings. If you need to refer to other file paths in your settings,
there are a few ways to handle this.

First, you can use Python's ``os.path`` module to set file paths relative to the
location of the settings.py file. For example::

    import os.path
    MEDIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))

You can also use the ``ENGAGE_APP_FILES_BASE`` setting defined in
engage_settings.py::

    import os.path
    import engage_settings
    MEDIA_ROOT = os.path.join(engage_settings.ENGAGE_APP_FILES_BASE,
                              "test_app_v1/test_app/media")

Settings for static content
~~~~~~~~~~~~~~~~~~~~~~~
Django provides a mechanism for serving static files (e.g. images,
JavaScript fles, and style sheets) directly from the
webserver, bypassing the Django framework. This is described in the
Django documentation at
https://docs.djangoproject.com/en/dev/howto/static-files/.

Engage supports this approach through special handling of the
``STATIC_URL``, ``STATIC_ROOT``, ``MEDIA_URL``, and ``MEDIA_ROOT``
settings. The STATIC_URL/STATIC_ROOT settings are used as follows:
 * If the ``STATIC_URL`` setting is defined to a non-empty value
   (e.g. ``/static/``), and the application
   ``django.contrib.staticfiles`` is included in ``INSTALLED_APPS``,
   then Engage will run the ``collectstatic`` management command as a
   part of deployment. This will gather all static content to the
   directory specified by ``STATIC_ROOT``  (``/static`` under your project root, by
   default). The webserver will then be configured to map any requests
   under ``STATIC_URL`` to the associated files under ``STATIC_ROOT``.
 * If ``STATIC_URL`` is defined to a non-empty value, the
   ``django.contrib.staticfiles`` application is *not* enabled, and
   ``STATIC_ROOT`` points to a location under your project root, then
   Engage will configure the webserver to map files under
   ``STATIC_URL`` to the associated files under ``STATIC_ROOT``. Since
   ``django.contrib.staticfiles`` is not enabled, the
   ``collectstatic`` command will not be run.

The ``MEDIA_URL`` and ``MEDIA_ROOT`` settings are used to define the
URL and directory for user-uploaded content,
respectively. Applications built for previous versions of Django
may also use these settings for static application-provided content as well. If both
settings are defined, Engage will configure the webserver to map requests from
``MEDIA_URL`` to ``MEDIA_ROOT``.

The ``STATIC_URL`` and ``MEDIA_URL`` settings are typically defined in
the settings file as a path (e.g. /static) rather than providing an
absolute  URL with hostname and port (e.g. http://localhost:8000/static).

The hostname and port for your application will be determined by Engage at
deployment time. If you do use an absolute URL in your settings file, you can just
put in an arbitrary hostname and port (e.g. something that works in your test
environment). When your deployed Django application starts, Engage will parse
the URLs for your settings, and if the URLs are absolute, replace the
hostname and port with ``ENGAGE_WEBSERVER_HOSTNAME`` and ``ENGAGE_WEBSERVER_PORT``.

The path component of the URLs in these two settings is expected by Django
to end in a trailing slash ('/'). If you forget this slash, Engage will add
it for you.


.. _fixtures:

Fixtures
--------
A Django "fixture" is a file containing data to be loaded into the database
when the database is being initialized. This can be basic data needed for
your application to function or test data. For more details on fixture
files, see the ``django-admin.py`` utility documentation, specifically 
http://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-loaddata
and http://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-dumpdata.

Engage can load fixture files as a part of your application's deployment.
Engage will run the ``syncdb`` command of ``django-admin.py`` to create your required
database tables. As a part of this process, ``syncdb`` will load any ``initial_data``
fixtures that it finds. If you have additional fixtures that you want loaded
during deployment, assign a tuple of fixture names to a variable called
``ENGAGE_APP_DB_FIXTURES`` in your settings file. For example::

    ENGAGE_APP_DB_FIXTURES = ("demo_data1", "demo_data2")

Engage will load these additional fixtures using the ``loaddata`` command of
``django-admin.py``.

Note that, for upgrades, Engage with *not* load any fixtures, in order
to avoid overwriting existing data in the application database.


Locating Fixture Files
~~~~~~~~~~~~~~~~~~~~~~
The ``django-admin.py`` utility has some rather complex rules for locating fixture
files. Engage uses a subset of these rules. Fixture files may be encoded using
either xml or json. The encoding may be specified using the file extensions
".xml" and ".json". If you leave off the encoding in your fixture name (e.g.
"test_data" instead of "test_data.json"), ``django-admin`` and Engage will look for
files with either extension.

Engage will search for fixture files in the following locations within your
application's directory structure:

#. If a fixture name evaluates to an absolute path in the filesystem, it will
   check if that file exists.
#. Next, it looks for a "fixtures" subdirectory in all the Python modules
   defined in your ``INSTALLED_APPS`` setting. Note that any referenced fixture
   files must be included in your application archive. Any files in an
   installed app not included in your archive (e.g. in django.contrib.auth)
   will not be found.
#. You can add more directories to search for fixtures using the Django setting
   ``FIXTURE_DIRS``.
#. Finally, a fixture name can be a relative path from the directory containing
   your settings file.

When preparing your application for deployment, the Engage SDK will check
that it can find all the fixtures referenced in ``ENGAGE_APP_DB_FIXTURES`` using
this search process.

.. _logging:

Logging
-------
Engage initializes the logging for your application, setting up a default log
handler which writes to a rotating logfile (whose name is available in
``engage_settings.ENGAGE_LOG_FILE``). This initialization is accomplished by
emulating the Django 1.3 ``LOGGING`` and ``LOGGING_CONFIG`` settings (see
http://docs.djangoproject.com/en/dev/ref/settings/#std:setting-LOGGING).
Engage will set LOGGING to None and LOGGING_CONFIG to a function to initialize
logging. When the settings file is loaded, this function is called.

Although you could override these settings, this is not recommended, as logging
to a different location can make it difficult to retrieve your logfiles from
genForma's servers.

The recommended way to set up logging for each module (Python file) is to
initialize a module-global variable as follows::

    import logging
    logger = logging.getLogger(__name__)


Upgrades
------------
If you wish to support schema changes in future versions of your
application, you need to create an initial migration script using
*South*. Details may be found in the :doc:`upgrading` section. 
