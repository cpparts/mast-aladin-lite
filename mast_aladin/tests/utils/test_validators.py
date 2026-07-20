import mast_aladin.utils.validators as validators


class TestUtils:
    def test_is_valid_s3_uri(self):
        uri = "s3://my-bucket/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is True

    def test_non_s3_uri(self):
        uri = "http://my-bucket/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is False

    def test_file_is_not_s3_uri(self):
        uri = "file:///path/to/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is False
