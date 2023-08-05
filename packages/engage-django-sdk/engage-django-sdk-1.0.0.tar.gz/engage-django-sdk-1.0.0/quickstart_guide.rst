==============================
Engage-Django Quickstart Guide
==============================

Using engage-django-sdk, you can upload your own Django application and
then deploy it in the cloud. Getting your application to run on the Engage
platform is quite simple. See the steps below for details.

Prerequisites
=============
First, a few simple preparation steps
are needed. These ensure that Engage can find the key files in your application
and that the application can be configured to run on Engage.

File Layout
-----------
Engage expects all the files of your Django project to be under one directory (we'll call this the *project
root directory*). This include application code, static files, etc. If you have dependencies on other Python
packages, you can list then in a ``requirements.txt`` file for installation via ``pip``.  See the
*SDK Reference Manual* for details.

The directory containing your Django settings module will be added to the ``PYTHONPATH`` on the
deployed system. For example, if your settings module is at ``my_application/app/settings.py`` and
you specify ``app.settings`` as your Django settings module, the ``my_application`` directory will be
added to your ``PYTHONPATH``. Any extra Python packages that you want to include with your
application should be added under this directory was well.

Django Settings
---------------
For most applications, you can just use your existing settings.py file, as long
as it does not contain any absolute file path references. Certain settings will
be overriden by Engage (e.g. the database configuration) to match the desired
server configuration. More details may be found in the *SDK Reference Manual*.

SDK Prerequisites
-----------------
We provide an SDK to validate your application and package it up for deployment.
This SDK is written in Python and requires Python 2.6.x or Python 2.7.x. It has
been tested on MacOSX and Linux. Installation of the SDK requires
setuptools (available at http://pypi.python.org/pypi/setuptools) and virtualenv
(available at http://pypi.python.org/pypi/virtualenv).

Currently, we support applications built for Django 1.3.


SDK installation
----------------
The SDK is available on the Python Package Index (http://pypi.python.org). You can install it directly
from PyPi using the easy_install utility::

  easy_install engage-django-sdk

This will install the ``engage-django`` command line utility into your Python distribution's bin directory.

You can also download the SDK from our website at http://beta.genforma.com/media/downloads/engage-django-sdk-1.0.0.tar.gz. 


Application Packaging
=====================
Now you are ready to run the packager command to prepare your application for
deployment. After installing the SDK, you can run the packager as follows::

    engage-django prepare-dir app_root_dir django_settings_module packaged_archive_filename

You provide three arguments to the prepare-dir command:

1. app_root_dir -- the root directory of your project, as described above in
   File Layout.
2. django_settings_module -- the name of the Python module containing your
   application's settings.
3. packaged_archive_filename -- the name of the packaged application archive
   file to be created. This should end in one of .tgz (gzipped tar archive),
   .tar.gz (gzipped tar archive), or .zip (zip archive). This is the file that
   you will upload to Engage.

If the packager finds any serious problems with your application, it will print
a description of the problem and exit without creating an archive file. If it
finds a potential problem that does not necessarily prevent deployment, it will just print
a warning and create the archive file.

Once you have your application archive file, you are ready to deploy.


Steps for Deployment
=============================

1. Start at http://beta.genforma.com/deploy/start/
2. Specify the filename of your application archive and select your desired
   configuration options.
3. Click the *Make it so!* button.
4. The deployment process has started. You will receive an email when deployment
   has completed (usually just five minutes or so). The email will contain the
   URL of your new application.
5. Login to your application with the user admin and the password you specified
   on the configuration page.


Need more help?
===============
For more information, take a look at the SDK reference manual at
http://beta.genforma.com/sdk_refman/index.html, the
support page at http://beta.genforma.com/support-django-demo.html, or email us at
support@genforma.com.
