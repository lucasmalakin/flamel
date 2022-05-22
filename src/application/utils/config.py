# -*- coding: utf-8 -*-

# standard modules
import os
import urllib.parse

credentials = {
    "aws": {
        "access_key_id": os.environ.get("ACCESS_KEY"),
        "secret_access_key": os.environ.get("SECRET_KEY"),
        "s3_region_name": os.environ.get("S3_REGION_NAME", "sa-east-1"),
    },
    "twitter": {"bearer_token": os.environ.get("BEARER_TOKEN")},
}

datalake_config = {
    "geolocation-twitter": {"s3_bucket": os.environ.get("BUCKET_GEOLOCATION")},
    "general-portuguese": {"s3_bucket": os.environ.get("BUCKET_GENERAL_PORTUGUESE")},
}
