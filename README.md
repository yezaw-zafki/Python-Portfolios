# Python Portfolios

Collection of data analysis and engineering projects.

## Load Customer Data from Amazon S3

`Load data from S3 bucket.py` downloads a customer CSV from Amazon S3 and
loads it into a pandas DataFrame named `customer_df` when the script runs.

### What the loader does

1. Reads the S3 object URI from `.env`.
2. Parses the URI into an S3 bucket and object key.
3. Uses `boto3` to download the object through the standard AWS credential
	 chain.
4. Parses the semicolon-delimited CSV using `latin1` encoding.
5. Prints the number of records and the first five rows as a verification.

### Requirements

Install the Python dependencies in the project virtual environment:

```bash
.venv/bin/pip install boto3 pandas python-dotenv
```

The loader expects Python 3.10 or newer because it uses modern type hints.

### Configuration

Create a local `.env` file with the S3 object location:

```dotenv
AWS_S3_STORAGE_CONNECTION="s3://your-bucket/path/to/Customers.csv"
AWS_DEFAULT_REGION="ap-southeast-2"
```

Do not commit `.env` or put access keys in it. Configure AWS credentials
locally instead:

```bash
aws configure
```

The IAM identity needs `s3:GetObject` permission for the specific CSV object.

Example least-privilege policy:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::your-bucket/path/to/Customers.csv"
		}
	]
}
```

### Run the loader

```bash
.venv/bin/python "Load data from S3 bucket.py"
```

Expected output includes a record count and a preview similar to:

```text
Loaded 793 customer records.
	Customer ID  Customer Name
0    AA-10315     Alex Avila
```

### Use the loader from another Python file

Import the function and assign the returned DataFrame:

```python
from importlib.machinery import SourceFileLoader

loader = SourceFileLoader("s3_loader", "Load data from S3 bucket.py").load_module()
customer_df = loader.load_customer_data()
```

Importing the module does not download data automatically; the download only
runs when the script is executed directly.
