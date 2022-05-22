# -*- coding: utf-8 -*-

# standard modules
from datetime import datetime, timedelta
from operator import index
import time
import os
import fsspec  # must be included
import uuid

# third-party modules
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import boto
import boto3
import s3fs

# custom modules
from application.utils.logger.log_manager import LogManager


class ParquetLoader(object):
    def __init__(
        self,
        is_pandas=False,
        is_table=False,
        compression="snappy",
        schema=None,
        defaults={},
    ):
        self.logger = LogManager.get_logger("Flamel")
        self.is_pandas = is_pandas
        self.compression_type = compression
        self.schema = schema
        self.defaults = defaults
        self.is_table = is_table
        boto3.resource(
            "s3",
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY"),
            region_name=os.getenv("S3_REGION_NAME"),
        )

    def save_s3_partitioned_parquet(self, data, s3_bucket, s3_folder, partition):
        self.generate_partitioned_parquet(
            data,
            s3_bucket=s3_bucket,
            s3_folder=s3_folder,
            partition_columns=partition,
        )

    def generate_partitioned_parquet(
        self, data, s3_bucket, s3_folder, partition_columns
    ):
        if len(data) == 0:
            return False

        start = time.time()

        if self.is_table:
            table = data
        else:
            table = self.generate_table(data)

        self.logger.warning("Uploading file to S3")

        fs = s3fs.S3FileSystem()
        bucket_uri = "s3://{bucket}/{folder}".format(bucket=s3_bucket, folder=s3_folder)
        pq.write_to_dataset(
            table,
            bucket_uri,
            filesystem=fs,
            partition_cols=partition_columns,
            use_dictionary=True,
            coerce_timestamps="ms",
            allow_truncated_timestamps=True,
            compression=self.compression_type,
            use_legacy_dataset=True,
        )

        end = time.time()
        self.logger.warning("Took %d seconds to upload file", (end - start))

    def generate_table(self, data):
        if not self.is_pandas:
            data = pd.DataFrame.from_dict(data)

        if self.schema is not None:
            for column in self.schema.names:
                if column not in data.columns:
                    data[column] = self.defaults.get(column, None)

            table = pa.Table.from_pandas(
                data,
                preserve_index=False,
                schema=self.schema,
            )
        else:
            table = pa.Table.from_pandas(data, preserve_index=False)

        return table

    def save_s3_parquet(self, data, file_name, s3_bucket, s3_folder):
        self.generate_parquet(
            data, file_name=file_name, s3_bucket=s3_bucket, s3_folder=s3_folder
        )

    def generate_parquet(self, data, file_name, s3_bucket, s3_folder):
        if len(data) == 0:
            return False

        start = time.time()

        table = self.generate_table(data)

        self.logger.warning("Uploading file to S3")

        file_name = file_name + ".parquet"
        fs = s3fs.S3FileSystem()
        bucket_uri = "s3://{bucket}/{folder}/{file_name}".format(
            bucket=s3_bucket, folder=s3_folder, file_name=file_name
        )
        pq.write_table(
            table,
            bucket_uri,
            filesystem=fs,
            use_dictionary=True,
            coerce_timestamps="ms",
            compression=self.compression_type,
            allow_truncated_timestamps=True,
        )

        end = time.time()
        self.logger.warning("Took %d seconds to upload file", (end - start))

    def read_parquet(self, s3_bucket, s3_folder, as_pandas=True, s3_key=""):
        try:
            # set S3 path
            if s3_key != "":
                s3_path = "/".join([s3_bucket, s3_key])
            else:
                s3_path = "/".join([s3_bucket, s3_folder])

            # download s3
            fs = s3fs.S3FileSystem()

            if as_pandas:
                data_frame = pq.read_table(source=s3_path, filesystem=fs).to_pandas()
            else:
                data_frame = pq.read_table(source=s3_path, filesystem=fs)

            return data_frame

        except Exception as e:
            print(e)
            raise

    def clear_folder(self, s3_bucket, s3_folder, host="s3.amazonaws.com"):
        conn = boto.connect_s3(
            os.getenv("ACCESS_KEY"),
            os.getenv("SECRET_KEY"),
            host=host,
        )

        bucket = conn.get_bucket(s3_bucket)
        for key in bucket.list(prefix=s3_folder):
            key.delete()

    def run_crawler(self, crawler_name, region="us-east-1"):
        glue_client = boto3.client("glue", region_name=region)
        glue_client.start_crawler(Name=crawler_name)

    def clear_date_partitions(
        self, days, s3_bucket, s3_folder, host="s3.amazonaws.com"
    ):
        today = datetime.utcnow()

        for day in range(days + 1):
            partition_to_remove = today - timedelta(days=day)
            self.clear_folder(
                s3_bucket=s3_bucket,
                s3_folder=s3_folder
                + "/year={}/month={}/day={}".format(
                    partition_to_remove.year,
                    partition_to_remove.month,
                    partition_to_remove.day,
                ),
                host=host,
            )

    @staticmethod
    def save_s3_parquet_from_local(
        local_path, s3_bucket, s3_key, compression_type="snappy"
    ):
        fs = s3fs.S3FileSystem()
        bucket_uri = "s3://{bucket}/{key}".format(bucket=s3_bucket, key=s3_key)

        table = pq.read_table(local_path)

        pq.write_table(
            table,
            bucket_uri,
            filesystem=fs,
            coerce_timestamps="ms",
            compression=compression_type,
            allow_truncated_timestamps=True,
        )

        return bucket_uri

    def pandas_s3(self, df, s3_bucket, project_name, s3_folder):
        fs = s3fs.S3FileSystem()
        with fs.open(
            f"{s3_bucket}/{project_name}/{s3_folder}/{uuid.uuid4().hex}.csv", "w"
        ) as f:
            df.to_csv(f, index=False)
