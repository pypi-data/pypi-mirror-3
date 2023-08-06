# Copyright (C) 2012 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Raven.
#
# LAVA Raven is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Raven is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with LAVA Raven.  If not, see <http://www.gnu.org/licenses/>.

"""
Raven extension for LAVA
"""

import logging

from lava_server.extension import HeadlessExtension


class RavenExtension(HeadlessExtension):
    """
    Extension for using Raven (Sentry) with LAVA
    """

    _DEFAULT_LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.handlers.SentryHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

    def contribute_to_settings_ex(self, settings_module, settings_object):
        """
        Enable and configure Raven if requested
        """
        SENTRY_DSN = settings_object.get_setting("SENTRY_DSN")
        if not SENTRY_DSN:
            logging.warning("This instance will not use sentry as SENTRY_DSN is"
                            " not configured")
            return
        settings_module['INSTALLED_APPS'].append('raven.contrib.django')
        # http://raven.readthedocs.org/en/latest/config/index.html#the-sentry-dsn
        settings_module['SENTRY_DSN'] = SENTRY_DSN
        # Set up the django logging framework
        settings_module['LOGGING'] = settings_object.get_setting(
            "LOGGING", self._DEFAULT_LOGGING)
        if settings_object.get_setting("USE_SENTRY_404_MIDDLEWARE"):
            # Enable 404 middleware if requested
            settings_module['MIDDLEWARE_CLASSES'] += (
                'raven.contrib.django.middleware.Sentry404CatchMiddleware',)
        if settings_object.get_setting("USE_SENTRY_RESPONSE_MIDDLEWARE"):
            # Enable response middleware if requested
            settings_module['MIDDLEWARE_CLASSES'] += (
                'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',)

    @property
    def name(self):
        return "Raven"

    @property
    def version(self):
        import lava.raven
        import versiontools
        return versiontools.format_version(
            lava.raven.__version__, hint=lava.raven)

    @property
    def description(self):
        return "Integrated error reporting via Sentry"
