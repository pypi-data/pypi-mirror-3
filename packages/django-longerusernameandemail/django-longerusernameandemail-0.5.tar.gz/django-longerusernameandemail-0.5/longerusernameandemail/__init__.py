from django.conf import settings


def MAX_USERNAME_LENGTH():
    return getattr(settings, "MAX_USERNAME_LENGTH", 255)
