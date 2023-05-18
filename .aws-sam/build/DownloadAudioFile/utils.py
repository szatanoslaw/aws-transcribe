import json
from typing import Dict
from urllib.parse import urlparse

from validators import validator


@validator
def validate_extension(path, allowed_extensions):
    file_format = path.split(".")[-1]
    if file_format in allowed_extensions:
        return True


def get_extension(path):
    return path.split(".")[-1]


def build_response(body, status_code: int = 200) -> Dict:
    return {"statusCode": status_code, "body": json.dumps(body)}


def parse_url_to_s3_uri(url: str) -> str:
    return "s3:/" + urlparse(url).path
