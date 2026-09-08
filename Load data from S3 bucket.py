import os
from io import BytesIO
from urllib.parse import urlparse

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv


S3_URI_ENV_VAR = "AWS_S3_STORAGE_CONNECTION"
CSV_ENCODING = "latin1"
CSV_SEPARATOR = ";"


def _parse_s3_uri(s3_uri: str) -> tuple[str, str]:
	"""Return the bucket and object key from an S3 URI."""
	parsed_uri = urlparse(s3_uri)
	if parsed_uri.scheme != "s3" or not parsed_uri.netloc or not parsed_uri.path:
		raise ValueError(
			f"{S3_URI_ENV_VAR} must be a valid s3://bucket/key URI."
		)

	return parsed_uri.netloc, parsed_uri.path.lstrip("/")


def load_customer_data() -> pd.DataFrame:
	"""Load the customer CSV configured by ``AWS_S3_STORAGE_CONNECTION``."""
	load_dotenv()

	s3_uri = os.getenv(S3_URI_ENV_VAR)
	if not s3_uri:
		raise ValueError(f"{S3_URI_ENV_VAR} is not set in the environment.")

	bucket, key = _parse_s3_uri(s3_uri)

	s3_client = boto3.client("s3")
	try:
		response = s3_client.get_object(
			Bucket=bucket,
			Key=key,
		)
	except NoCredentialsError as error:
		raise RuntimeError(
			"AWS credentials are missing. Configure the AWS credential chain "
			"before loading the S3 object."
		) from error
	except ClientError as error:
		error_code = error.response.get("Error", {}).get("Code", "unknown")
		raise RuntimeError(
			f"Unable to read s3://{bucket}/{key} from S3 ({error_code}). "
			"Check the IAM policy and bucket permissions."
		) from error

	return pd.read_csv(
		BytesIO(response["Body"].read()),
		encoding=CSV_ENCODING,
		sep=CSV_SEPARATOR,
	)


def main() -> None:
	"""Load the customer data and display a small verification preview."""
	customer_df = load_customer_data()
	print(f"Loaded {len(customer_df):,} customer records.")
	print(customer_df.head())


if __name__ == "__main__":
	main()
