# ETL Data Pipeline

This project builds a small data warehouse from CRM and ERP CSV files stored in Azure Blob Storage. The notebook extracts the raw files, cleans and standardizes the data, validates business rules, and loads the final tables into MySQL.

The workflow is organized in [ETL.ipynb](ETL.ipynb):

1. **Extract** source files from Azure Blob Storage.
2. **Transform** and standardize the raw data.
3. **Validate** the cleaned data against quality rules.
4. **Load** the final DataFrames into MySQL.

## Project Goal

The source data comes from two operational systems:

- **CRM**: customer, product, and sales transaction data.
- **ERP**: customer demographics, customer locations, and product categories.

The source systems use different column names, date formats, identifiers, and coded values. This ETL process creates consistent DataFrames for reporting, analysis, and data modeling.

## Pipeline Structure

```text
Azure Blob Storage
        |
        v
extract_data()
        |
        v
transform_data(raw_data)
        |
        v
validate_data(cleaned_data)
        |
        v
load_data(cleaned_data)
        |
        v
MySQL database: baraa_v2
```

Each stage receives data as an argument and returns a result. This avoids hidden global state and makes the pipeline easier to test, rerun, and extend.

## Source Files

All files are stored in the Azure Blob Storage container `baraa`.

### CRM Sources

| File | Description |
| --- | --- |
| `source_crm/cust_info.csv` | CRM customer master data |
| `source_crm/prd_info.csv` | CRM product master data |
| `source_crm/sales_details.csv` | CRM sales transactions |

### ERP Sources

| File | Description |
| --- | --- |
| `source_erp/CUST_AZ12.csv` | ERP customer demographics |
| `source_erp/LOC_A101.csv` | ERP customer locations |
| `source_erp/PX_CAT_G1V2.csv` | ERP product categories |

## 1. Extract

### `read_blob_csv()`

`read_blob_csv()` reads one CSV file from Azure Blob Storage. It receives the container name, blob path, and Azure connection string, then returns a pandas DataFrame.

### `extract_data()`

`extract_data()` defines the source-file mapping and reads all six files. It returns the raw data in one dictionary:

```python
raw_data = {
    "crm_customer": ...,
    "crm_product": ...,
    "crm_sales": ...,
    "erp_customer": ...,
    "erp_location": ...,
    "erp_category": ...,
}
```

The Azure connection is configured through `.env`:

```env
AZURE_STORAGE_CONNECTION_STRING=...
```

Extraction does not change the source values. Keeping extraction separate makes it possible to review the original data before applying cleaning rules.

## 2. Transform

### `transform_data(raw_data)`

`transform_data()` calls the correct cleaning function for each source and returns the cleaned DataFrames in `cleaned_data`.

The output DataFrames are:

| Source | DataFrame | Purpose |
| --- | --- | --- |
| CRM customer | `df_customer` | Customer master data |
| CRM product | `df_product` | Product master data |
| CRM sales | `df_sales` | Sales transactions |
| ERP customer | `df_customer_erp` | Customer demographics |
| ERP location | `df_location` | Customer locations |
| ERP category | `df_category` | Product category reference |

### CRM Customer: `clean_customer_data()`

This function:

- Removes duplicate rows.
- Removes rows without `cst_id` or `cst_key`.
- Converts `cst_id` to an integer.
- Converts `cst_create_date` to a date.
- Keeps the latest record for each customer.
- Trims customer first and last names.
- Renames `cst_firstname2` to `cst_firstname`.
- Renames `cst_lastname2` to `cst_lastname`.
- Converts marital codes `M` and `S` to `Married` and `Single`.
- Converts gender codes `M` and `F` to `Male` and `Female`.
- Uses `N/A` for missing standardized categorical values.

### CRM Product: `clean_product_data()`

This function:

- Removes duplicates and rows without product identifiers.
- Extracts `cat_id` from the product key.
- Replaces the category-key separator `-` with `_`.
- Replaces missing product cost with `0`.
- Converts product-line codes:
  - `M` to `Mountain`
  - `R` to `Road`
  - `S` to `Other Sale`
  - `T` to `Touring`
- Converts product start and end fields to dates.
- Sorts records by product key and start date.
- Repairs records where the start date is after the end date by using the next start date minus one day.

### CRM Sales: `clean_sales_data()`

This function creates `df_sales`.

#### Order numbers

The source format is `SO` followed by five digits, such as `SO43697`. Values that do not match this format become `NULL`.

#### Dates

The fields `sls_order_dt`, `sls_ship_dt`, and `sls_due_dt` are parsed from `YYYYMMDD`. Dates outside 1900 through 2050 become invalid. The final values contain dates only, without timestamps.

The process checks that:

- Order date is not later than ship date.
- Order date is not later than due date.

#### Quantity and price

- Positive whole-number quantities are preserved.
- The source quantity is mostly `1`; this reflects the source data and is not imposed by the transformation.
- Missing, nonnumeric, zero, negative, or fractional quantities become `0`.
- Prices are converted to numeric values.
- Negative prices are normalized with `abs()`.

#### Sales calculation

The existing sales value is replaced with the business formula:

```text
sls_sales = sls_quantity * sls_price
```

This guarantees that the final sales value agrees with the cleaned quantity and price.

### ERP Customer: `clean_erp_customer_data()`

This function creates `df_customer_erp` and:

- Removes the `NAS` prefix from `CID`.
- Converts `BDATE` to a date.
- Replaces invalid or future birth dates with `NaT`.
- Standardizes gender values to `Male`, `Female`, or `N/A`.
- Accepts code and text forms such as `M`, `F`, `Male`, and `Female`.

### ERP Location: `clean_erp_location_data()`

This function creates `df_location` and:

- Replaces hyphens in `CID` with underscores.
- Trims whitespace.
- Replaces `DE` with `Germany`.
- Replaces `US` and `USA` with `United State`.
- Leaves all other non-null country values unchanged.
- Replaces null or blank country values with `N/A`.

### ERP Category

The category source is already suitable for use. It is copied into `df_category` without business transformation.

## Standardization

`normalize_dataframe()` is applied to every cleaned DataFrame after source-specific transformations.

It:

- Converts every column name to `snake_case`.
- Preserves acronyms correctly, such as `CID` becoming `cid` rather than `c_i_d`.
- Converts detected date fields to date-only values.
- Applies the same final formatting across CRM and ERP outputs.

## 3. Validate

### `validate_data(cleaned_data)`

This function runs quality checks before loading and returns a validation report.

The checks include:

- Invalid sales order numbers.
- Sales order, ship, and due-date relationships.
- Invalid sales quantities.
- Negative sales prices.
- Product start-date and end-date violations.
- Future ERP birth dates.
- Allowed ERP gender values.
- Country values replaced with `N/A`.

Validation is separate from transformation. Transformation changes the data; validation confirms that the result follows the expected rules.

## 4. Load

### `load_data(cleaned_data)`

This function loads the cleaned DataFrames into MySQL database `baraa_v2`.

MySQL settings are read from `.env`:

```env
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_PORT=3306
```

The loader:

1. Connects to the MySQL server.
2. Creates `baraa_v2` if it does not exist.
3. Temporarily disables foreign-key checks.
4. Drops the existing target tables.
5. Appends each cleaned DataFrame to its target table.
6. Restores foreign-key checks.
7. Runs `SHOW TABLES` to verify the load.

### Target Tables

| DataFrame | MySQL table |
| --- | --- |
| `df_customer` | `dim_customer` |
| `df_product` | `dim_product` |
| `df_sales` | `fact_sales` |
| `df_customer_erp` | `dim_customer_erp` |
| `df_location` | `dim_location` |
| `df_category` | `dim_category` |

The load is repeatable because the target tables are rebuilt from the current cleaned DataFrames.

## Recommended Run Order

Run the notebook from top to bottom:

1. Run imports and environment configuration.
2. Run `extract_data()` to create `raw_data`.
3. Run the cleaning functions and `transform_data(raw_data)`.
4. Run `validate_data(cleaned_data)`.
5. Review the validation report.
6. Run `load_data(cleaned_data)` after validation passes.

Do not load the data when validation reports unexpected errors. Review the source data or the relevant cleaning function first.

## Design Principles

- Keep extraction, transformation, validation, and loading separate.
- Pass data through function arguments and return values.
- Preserve raw data until transformation begins.
- Keep source-specific rules in source-specific functions.
- Apply shared formatting in one normalization function.
- Keep validation visible and repeatable.
- Keep credentials in `.env`, never in notebook code or documentation.
- Use clear DataFrame and database table names.
