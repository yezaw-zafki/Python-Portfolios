import os
from io import BytesIO
from urllib.parse import urlparse
from typing import Any

import boto3
import pandas as pd
from botocore.exceptions import (
	ClientError,
	NoCredentialsError,
	PartialCredentialsError,
)
from dotenv import load_dotenv

CSV_ENCODING = "latin1"
CSV_SEPARATOR = ";"


def _parse_s3_uri(s3_uri: str) -> tuple[str, str]:
	"""Return the bucket and object key from an S3 URI."""
	parsed_uri = urlparse(s3_uri)
	if (
		parsed_uri.scheme != "s3"
		or not parsed_uri.netloc
		or not parsed_uri.path.strip("/")
		or parsed_uri.query
		or parsed_uri.fragment
	):
		raise ValueError("s3_uri must be a valid s3://bucket/key URI.")

	return parsed_uri.netloc, parsed_uri.path.lstrip("/")


def load_s3_csv(
	s3_uri: str,
	*,
	encoding: str = CSV_ENCODING,
	sep: str = CSV_SEPARATOR,
	dtype: Any | None = None,
	usecols: Any | None = None,
	**read_csv_kwargs: Any,
) -> pd.DataFrame:
	"""Load a CSV object from S3 into a pandas DataFrame.

	The boto3 client uses the standard AWS credential chain. Additional keyword
	arguments are passed to ``pandas.read_csv``.
	"""
	bucket, key = _parse_s3_uri(s3_uri)
	s3_client = boto3.client("s3")

	try:
		response = s3_client.get_object(
			Bucket=bucket,
			Key=key,
		)
	except (NoCredentialsError, PartialCredentialsError) as error:
		raise RuntimeError("AWS credentials are missing or incomplete.") from error
	except ClientError as error:
		error_code = error.response.get("Error", {}).get("Code", "unknown")
		location = f"s3://{bucket}/{key}"
		if error_code in {"AccessDenied", "403"}:
			raise PermissionError(f"Access denied when reading {location}.") from error
		if error_code in {"NoSuchKey", "NoSuchBucket", "404"}:
			raise FileNotFoundError(f"S3 object or bucket was not found: {location}.") from error
		raise RuntimeError(f"Unable to read {location} from S3 ({error_code}).") from error

	body = response["Body"]
	try:
		return pd.read_csv(
			BytesIO(body.read()),
			encoding=encoding,
			sep=sep,
			dtype=dtype,
			usecols=usecols,
			**read_csv_kwargs,
		)
	except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
		raise ValueError(f"Unable to parse CSV data from s3://{bucket}/{key}.") from error
	finally:
		body.close()


def main() -> None:
	"""Load the CSV URI in ``S3_CSV_URI`` and display a preview."""
	load_dotenv()
	s3_uri = os.getenv("S3_CSV_URI")
	if not s3_uri:
		raise ValueError("S3_CSV_URI is not set in the environment.")

	dataframe = load_s3_csv(s3_uri)
	print(f"Loaded {len(dataframe):,} records from {s3_uri}.")
	print(dataframe.head())


if __name__ == "__main__":
	main()