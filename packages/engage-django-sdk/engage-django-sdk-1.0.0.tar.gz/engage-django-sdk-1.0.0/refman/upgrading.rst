Upgrading
=========

Upgrades without Database Schema Changes
------------------------------------------------------------
If there are no changes to the database schema between versions, you
can simply package up the new version of your application and use the
``upgrade`` option on the status page at
http://beta.genforma.com/deploy/deploy_status/.

Engage will install the new application files, bringing over the
original version of your database.


Upgrades with Database Schema Changes
----------------------------------------------------------------
Supporting database schema changes is more complex. Engage leverages
the *South* schema migration tool (http://south.aeracode.org/) to
accomplish this. We will now look in more detail about how to use
South with Engage.

When using South, you need to package *schema migration* scripts with
each version of your application. These convert the database schema
from the previous version to match the current version. Luckily, South
helps you to create these scripts.

Preparation
~~~~~~~~~~~~~~
You need to install
South into your local Python environment and add it to the
``INSTALLED_APPS`` setting in your Django application. This will add
the various management commands provided by South to your Django
administration utility.

Initial Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When creating the first version of your application, you need to
include an initial migration script. This records in South's metadata tables
the initial schema as a basis for future comparisons. You run the
``schemamigration`` command with the ``--initial`` option to create
the initial migration script. See the South documentation for
details. The tutorial
(http://south.aeracode.org/docs/tutorial/part1.html) is a good
starting point.

The migration scripts should be packaged under your application in a
``migrations`` sub-module. This can be seen in the ``migrations``
directory of the :ref:`running_example` layout.

To indicate that you wish to perform schema migrations on an
application, you must add 'south' to the ``INSTALLED_APPS`` Django
setting.  You can now package and deploy your application. During
deployment, Engage will install South and run the ``migrate``
command.

If you desire additional validation of your application prior to
deployment, you can add the ``ENGAGE_MIGRATION_APPS``
to your Django settings file, providing a tuple containing the names of the
specific applications to be migrated. For our example application, we
would define the setting as follows::

  ENGAGE_MIGRATION_APPS = ('test_app.app',)

This will cause the validator to perform some additional checks.


Subsequent Versions
~~~~~~~~~~~~~~~~~~~~~~~~~
When changes are made an application that involve modifications to its
database schema, a new South migration script must be created. This is
done by re-running the ``schemamigration`` command. For additive
changes, it is usually sufficient to run with the ``--auto``
option. South will prompt interactively for input in situations where
it needs additional information (e.g. default values for existing
rows). The new migration scripts will be placed in the ``migrations``
package, along side the initial migration.

After adding the migration script, you can package a new version of
your application and deploy it to genForm using the *upgrade* link on
the status page. Engage will deploy the new version of your
application. It will upgrade your original database to the new schema
by running the South ``migration`` command.


Upgrade Rollback
-------------------------
For both types of upgrades, Engage performs a full backup of your
application before initiating the upgrade. If a problem occurs during
the upgrade process, the application will be automatically rolled back
to the previous version.


Testing Upgrades
----------------------------
Even though Engage can roll back a failed upgrade, it is recommend
that you test your upgrade before applying it to your production
application. This can be done by deploying a new application instance
with the previous version of the application, applying the upgrade to
that instance, and then validating that the upgrading application is
working correctly.
