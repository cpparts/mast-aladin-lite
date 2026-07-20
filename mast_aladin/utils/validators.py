from urllib.parse import urlparse


def is_valid_s3_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    # Check scheme is 's3' and a bucket name exists in netloc
    return parsed.scheme == 's3' and bool(parsed.netloc)
