from django.conf import settings
import django


def configure_settings():
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=['npm'],
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
    )
    django.setup()
