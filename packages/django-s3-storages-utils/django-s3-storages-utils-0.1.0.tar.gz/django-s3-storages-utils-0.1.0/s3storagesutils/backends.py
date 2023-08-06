from django.conf import settings
from .cached import CachedS3BotoStorage


class StaticCachedS3BotoStorage(CachedS3BotoStorage):
    def __init__(self, *args, **kwargs):
        settings_location = getattr(settings, 'STATIC_S3_STORAGE_LOCATION',
                None)
        if not 'location' in kwargs:
            kwargs['location'] = settings_location
        super(StaticCachedS3BotoStorage, self).__init__(*args, **kwargs)


class MediaCachedS3BotoStorage(CachedS3BotoStorage):
    def __init__(self, *args, **kwargs):
        settings_location = getattr(settings, 'MEDIA_S3_STORAGE_LOCATION',
                None)
        if not 'location' in kwargs:
            kwargs['location'] = settings_location
        super(MediaCachedS3BotoStorage, self).__init__(*args, **kwargs)
