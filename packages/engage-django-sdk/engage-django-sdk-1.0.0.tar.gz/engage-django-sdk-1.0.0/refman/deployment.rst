Preparing for Deployment
========================
The next step after reviewing your application is to use the Engage Django SDK
to validate your application and package it up for deployment.

Prerequisites
-------------
The SDK is written in Python and requires Python 2.6.x or Python 2.7.x. It has
been tested on MacOSX and Linux. The SDK is installed using setuptools
(http://pypi.python.org/pypi/setuptools), so you need to have that
installed in your Python environment. The packaging process also makes use
of the *virtualenv* utility (http://pypi.python.org/pypi/virtualenv).
If you do not pre-install virtualenv into your Python environment, it
will be installed as a dependency to the SDK.


Installation
------------
The SDK is available on the Python Package Index (http://pypi.python.org). You can install it directly
from PyPi using the easy_install utility::

  easy_install engage-django-sdk

This will install the ``engage-django`` command line utility into
your Python distribution's bin directory.  You can use the ``pip``
installer as well.

You can also download the SDK from our website at
http://beta.genforma.com/doc-django-quickstart.html or from PyPi.
Given a local copy of the SDK, you can install it in your Python
environment by specifying the archive file as an argument
to ``easy_install``.


Using the SDK
-------------
If the ``bin`` directory of your Python distribution is in your
``PATH``, you should be able to run the ``engage-django`` utility
directly from the command line.  You can verify this as follows::

  engage-django --help

In general, the utility expects the following on the command line::

   engage-django [options] COMMAND [ARGS]

where:
 * [options] is options for the utility. Currently --help and --verbose are supported.
 * COMMAND is the operation to perform. Valid commands are help,
   prepare-dir, and prepare-archive.
 * [ARGS] is used by some commands that take a fixed number of additional arguments.

As an example, the ``help`` command will print the required arguments and
description for another SDK command. The ``help`` command takes one additional
argument: the name of the command for which you want help. You can
print help for the ``prepare-dir`` command as follows::

    engage-django help prepare-dir


.. _application_packaging:

Application Packaging
---------------------
Now you are ready to run the packager command to prepare your application for
deployment. You can run the packager as follows::

    engage-django prepare-dir app_root_dir django_settings_module packaged_archive_filename

You provide three arguments to the ``prepare-dir`` command:

1. ``app_root_dir`` - the root directory of your project, as described
   in :ref:`file_layout`.
2. ``django_settings_module`` - the name of the Python module containing your application's
   settings.
3. ``packaged_archive_filename`` - the name of the packaged application archive file
   to be created. This should end in one of .tgz (gzipped tar archive), .tar.gz
   (gzipped tar archive), or .zip (zip archive). This is the file that you will
   upload to Engage.

If the packager finds any serious problems with your application, it will print
a description of the problem and exit without creating an archive file. If it
finds a potential problem that does not necessarily prevent deployment, it will just print a
warning and create the archive file.

If you already have your application available as an archive file, you can
use the ``prepare-archive`` command instead of ``prepare-dir``. This command will
perform the same validations on your application and modify your archive file
to add the necessary additional files.

Once you have a validated and packaged application archive file, you are ready
to deploy your application at http://beta.genforma.com/deploy/start.

Validation Checks
~~~~~~~~~~~~~~~~~
Now, we look into more detail at the validation checks that are performed.
The prepare commands first run the following basic checks:

* If ``prepare-dir``, the application directory must exist.
* If ``prepare-archive``, the input file must be a valid (gzipped) tar file or zip
  archive. Also, all entries in the archive must use a relative pathname and
  fall under a common root directory.
* The directory tree and Python files corresponding to your Django settings module must
  exist either at or under the application root directory. 

Next, the validator imports your settings file and performs the following
checks:

* If any settings provided by Engage (e.g. ``ADMINS``) are overridden (e.g. using
  ``ADMINS_OVERRIDE``), a warning is printed.
* Settings that contain filesystem paths are checked to see that they are
  either left at their default value or reference a file/directory under the
  application root directory (using a relative path). If this is not the case,
  an error is printed and the prepare command will fail. The following settings
  are checked in this way: ``MEDIA_ROOT``, ``STATIC_ROOT``.
* Some settings may contain a tuple of filesystem paths. These are checked to
  see if each element of the tuple points to a valid directory that is under
  the application root directory (using a relative path). The following
  settings are checked in this way: ``TEMPLATE_DIRS``, ``FIXTURE_DIRS``.
* If the user specifies the setting ``ENGAGE_APP_DB_FIXTURES``, each element of
  the tuple is checked to see if the associated fixture file can be found
  using the rules described in :ref:`fixtures`.
* Settings that contain absolute URLs are checked to see that the URLs are
  parse-able (by the urlparse module). The following settings are checked in
  this way: ``MEDIA_URL``, ``STATIC_URL``, ``ADMIN_MEDIA_PREFIX``.
* Verify that the Python modules referenced by the ``INSTALLED_APPS`` settings
  are all either provided under the application root directory, are  included
  in the standard Django distribution (usually under django.contrib),
  or provided by a package referenced in ``requirements.txt``.
