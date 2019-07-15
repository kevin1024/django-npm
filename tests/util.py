import os

from django.conf import settings
import django


def configure_settings():
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=['npm'],
        NPM_EXECUTABLE_PATH=os.environ.get('NPM_EXECUTABLE_PATH', 'npm'),
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
    )
    django.setup()
