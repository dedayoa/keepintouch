'''
Created on Aug 25, 2016

@author: Dayo
'''

import os

# In the event you decide to store uploaded contact files or uploaded custom data files
# to S3, remember to uncomment the below. Also fix all the "open"s as they currently expect to open from
# local on-disk storage
 
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# The region to connect to when storing files.
AWS_REGION = "us-east-1"

# The AWS access key used to access the storage buckets.
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','')

# The AWS secret access key used to access the storage buckets.
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','')

# The S3 bucket used to store uploaded files.
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME','')
