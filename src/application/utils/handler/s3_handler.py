# -*- coding: utf-8 -*-

# standard modules
import subprocess
import json
import time

# custom modules
from application.utils.logger.log_manager import LogManager


class S3Handler(object):
    def __init__(self, aws_cli: str = "aws_cli"):
        self._aws_cli = aws_cli
        self.logger = LogManager.get_logger("Flamel")

    def cmd_cli(self, cmd):
        i = 0
        exception = None
        while i < 3:
            try:
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                return result.decode("utf-8")
            except Exception as e:
                self.logger.warning("Exception {}".format(e))
                i += 1
                time.sleep(1)
                exception = e
                continue

        raise Exception(exception)

    def remove_s3_cli(self, path, region):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "rm",
            "s3://{}".format(path),
            "--recursive",
            "--region",
            region,
        ]
        return self.cmd_cli(cmd)

    def move_bucket_s3_cli(
        self,
        paths=("path_from", "path_to"),
        regions=("region_from", "region_to"),
    ):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "sync",
            "s3://{}".format(paths[0]),
            "s3://{}".format(paths[1]),
            "--source-region",
            regions[0],
            "--region",
            regions[1],
        ]
        return self.cmd_cli(cmd)

    def sync_bucket_s3_cli(self, paths=("path_from", "path_to")):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "sync",
            "s3://{}".format(paths[0]),
            "s3://{}".format(paths[1]),
            "--delete",
        ]
        return self.cmd_cli(cmd)

    def sync_bucket_s3_to_local(self, path_from, folder_local):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "sync",
            "s3://{}".format(path_from),
            folder_local,
        ]
        return self.cmd_cli(cmd)

    def list_s3_objects(self, bucket, prefix, path=""):
        cmd = [
            f"{self._aws_cli}",
            "s3api",
            "list-objects-v2",
            "--bucket",
            bucket,
            "--prefix",
            prefix,
        ]
        objects = self.cmd_cli(cmd)
        return json.loads(objects)["Contents"]

    def copy_s3_object(self, path_from, path_local):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "cp",
            "s3://{}".format(path_from),
            path_local,
            "--recursive",
        ]
        return self.cmd_cli(cmd)

    def copy_local_to_s3(self, local_path, s3_path):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "cp",
            local_path,
            "s3://{}".format(s3_path),
        ]
        return self.cmd_cli(cmd)

    def copy_exclude_s3_object(self, path_from, path_local, exclude):
        cmd = [
            f"{self._aws_cli}",
            "s3",
            "cp",
            "s3://{}".format(path_from),
            path_local,
            "--recursive",
            "--exclude",
            exclude,
        ]
        return self.cmd_cli(cmd)
