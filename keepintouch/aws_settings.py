'''
Created on Aug 25, 2016

@author: Dayo
'''

import os


DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"

# The region to connect to when storing files.
AWS_REGION = "us-east-1"

# The AWS access key used to access the storage buckets.
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','')

# The AWS secret access key used to access the storage buckets.
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','')

# The S3 bucket used to store uploaded files.
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME','')

# The S3 calling format to use to connect to the bucket.
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"

# The host to connect to (only needed if you are using a non-AWS host)
AWS_S3_HOST = "s3.us-east-1.amazonaws.com"

# A prefix to add to the start of all uploaded files.
AWS_S3_KEY_PREFIX = ""

# Whether to enable querystring authentication for uploaded files.
AWS_S3_BUCKET_AUTH = True

# The expire time used to access uploaded files.
AWS_S3_MAX_AGE_SECONDS = 60*60  # 1 hour.

# A custom URL prefix to use for public-facing URLs for uploaded files.
AWS_S3_PUBLIC_URL = ""

# Whether to set the storage class of uploaded files to REDUCED_REDUNDANCY.
AWS_S3_REDUCED_REDUNDANCY = False

# A dictionary of additional metadata to set on the uploaded files.
# If the value is a callable, it will be called with the path of the file on S3.
AWS_S3_METADATA = {}

# Whether to enable gzip compression for uploaded files.
AWS_S3_GZIP = True

#### STATIC FILE CONFIG


# The S3 bucket used to store static files.
AWS_S3_BUCKET_NAME_STATIC = ""

# The S3 calling format to use to connect to the static bucket.
AWS_S3_CALLING_FORMAT_STATIC = "boto.s3.connection.OrdinaryCallingFormat"

# The host to connect to for static files (only needed if you are using a non-AWS host)
AWS_S3_HOST_STATIC = ""

# Whether to enable querystring authentication for static files.
AWS_S3_BUCKET_AUTH_STATIC = False

# A prefix to add to the start of all static files.
AWS_S3_KEY_PREFIX_STATIC = ""

# The expire time used to access static files.
AWS_S3_MAX_AGE_SECONDS_STATIC = 60*60*24*365  # 1 year.

# A custom URL prefix to use for public-facing URLs for static files.
AWS_S3_PUBLIC_URL_STATIC = ""

# Whether to set the storage class of static files to REDUCED_REDUNDANCY.
AWS_S3_REDUCED_REDUNDANCY_STATIC = False

# A dictionary of additional metadata to set on the static files.
# If the value is a callable, it will be called with the path of the file on S3.
AWS_S3_METADATA_STATIC = {}

# Whether to enable gzip compression for static files.
AWS_S3_GZIP_STATIC = True