import os

if os.getenv('DJANGO_SETTINGS_MODULE'):
    from asv_utils.dj.media.settings import Settings
    settings = Settings()
#
