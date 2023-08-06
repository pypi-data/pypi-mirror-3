Raven support for LAVA
======================

This very small extension hooks up your LAVA system to Sentry via Raven, the
official Sentry client. 

Installation
^^^^^^^^^^^^

You first need to deploy sentry itself somewhere (I recommend the standalone
mode). Installing this extension is rather easy::

    $ pip install lava-raven

You need to edit your LAVA ``settings.conf``
(``/srv/lava/instances/.../etc/lava-server/settings.conf``) and define the
``SENTRY_DSN`` variable. You can get it from a running Sentry instance, follow
those steps::

1. Create a sentry user, sign in as that user
2. Click projects->manage
3. Select the desired sentry project (or just pick the default one)
4. Add yourself as a member. This allowed me to have the DSN variable.

Options
^^^^^^^

There are two conifguration options available, both are off by default:

USE_SENTRY_404_MIDDLEWARE 
*************************

If you flip this to ``true`` all 404 error will be reported in Sentry.

USE_SENTRY_RESPONSE_MIDDLEWARE
******************************

If you flip this to ``true`` all crashing views will be handled by sentry with
a nice error message that contains the incidend ID.

