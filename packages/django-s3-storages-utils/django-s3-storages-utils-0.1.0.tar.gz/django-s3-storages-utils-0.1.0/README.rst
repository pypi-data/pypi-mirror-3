s3-storages-utils - Utilities for S3+django-storages
====================================================

A simple app that allows a bit more control over the S3BotoStorage provided by
django-storages

It's use is fairly simple. Just put this in your settings::
    
    # Store the static files in the directory `static` in the S3 bucket
    STATIC_S3_STORAGE_LOCATION = 'static'
    
    # Store the media files in the directory `media` in the S3 bucket
    MEDIA_S3_STORAGE_LOCATION = 'media'

    DEFAULT_FILE_STORAGE = 's3storagesutils.MediaCachedS3BotoStorage'
    STATICFILES_STORAGE = 's3storagesutils.StaticCachedS3BotoStorage'

    # If you're using compressor
    COMPRESS_STORAGE = STATICFILES_STORAGE

That's all for now!
