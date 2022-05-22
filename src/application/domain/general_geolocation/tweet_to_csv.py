# -*- coding: utf-8 -*-

# standard modules
import os

# build-in modules
import pandas as pd

# custom modules
from application.utils.logger.log_manager import LogManager
from application.utils.handler.s3_handler import S3Handler
from application.utils.handler.parquet_loader import ParquetLoader

logger = LogManager.get_logger("Flamel")
s3_h = S3Handler()

s3_bucket = os.environ["BUCKET_GEOLOCATION"]
s3_folder = "tweet"

object_list = s3_h.list_s3_objects(bucket=s3_bucket, prefix=s3_folder)

pl = ParquetLoader()

columns_list = pl.read_parquet(
    s3_bucket=s3_bucket, s3_folder="", s3_key=object_list[1]["Key"]
).columns.tolist()

df_complete = pd.DataFrame(columns=[*columns_list])

for item in object_list:
    logger.warning(f"Item: {item}")
    if len(item["Key"]) >= 10:
        df = pl.read_parquet(s3_bucket=s3_bucket, s3_folder="", s3_key=item["Key"])
        df = df.dropna(axis=0, how="all")
        df_complete = pd.concat([df_complete, df])

df_complete = df_complete.drop_duplicates()

pl.pandas_s3(
    df=df_complete, s3_bucket=s3_bucket, project_name="merged", s3_folder=s3_folder
)
