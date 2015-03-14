from django.conf import settings

def configure_settings():
    try:
        settings.configure(
            DEBUG=True,
            CACHES = {
                'default': {
                    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
                }
            }
        )
    except RuntimeError:
        pass

