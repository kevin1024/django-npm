# -*- coding: utf-8 -*-


def configure_settings():
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        },
    )
