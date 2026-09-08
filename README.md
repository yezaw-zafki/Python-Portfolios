# Data Analysis Portfolio

This portfolio shows how I use data to answer business questions, improve data
quality, and create information that people can trust. Each project starts
with a real-world style dataset and ends with a clear result that could help a
team make better decisions.

## What This Portfolio Shows

- Careful data cleaning and organization.
- Clear answers to business questions.
- Charts and summaries that are easy to understand.
- Repeatable processes instead of one-time manual work.
- Experience working with files, cloud storage, and databases.

## Projects

### 1. Online Sales Analysis

File: [Exploratory Data Analysis EDA.ipynb](Exploratory%20Data%20Analysis%20EDA.ipynb)

I reviewed online sales data to understand what was happening in the business.
The analysis looks at:

- Total revenue, number of orders, and average order value.
- The product categories that sell the most.
- The regions with the strongest results.
- Changes in revenue and orders over time.
- How discount levels relate to sales and order value.
- The relationship between delivery time, customer ratings, and sales.

Before analyzing the data, I removed an incomplete date record and checked the
data structure. I then created summaries and charts so a manager could quickly
see strong areas and possible opportunities to improve customer experience.

**What this demonstrates:** business thinking, data cleaning, performance
measurement, chart creation, and communicating findings clearly.

### 2. Customer and Sales Data Pipeline

File: [ETL.ipynb](ETL.ipynb)

This project brings together customer, product, and sales files from two
different business systems. The data uses different names and formats, so I
organized it into one consistent set of tables.

The project:

1. Collects the original files.
2. Cleans names, dates, customer details, products, and sales values.
3. Checks for problems such as invalid dates, missing identifiers, and unusual
   prices or quantities.
4. Saves the trustworthy results in a database for future reporting.

The final information is arranged so that customer details, product details,
locations, categories, and sales can be reviewed separately or combined for
reporting.

**What this demonstrates:** attention to detail, reliable data preparation,
quality checking, and building a process that can be repeated.

### 3. Passenger Data Organization

File: [Data Modeling.ipynb](Data%20Modeling.ipynb)

I cleaned a passenger dataset and organized it into simple connected tables.
One table stores passenger details, another stores embarkation locations, and
another stores voyage information such as survival, ticket, fare, and cabin.

This makes the information easier to search, update, and use for questions such
as which passenger groups or travel details are linked to different outcomes.
I also checked that the cleaned data was successfully written to the database.

**What this demonstrates:** structured thinking, data organization, database
work, and careful checking of results.

### 4. Customer Data from Cloud Storage

File: [Load data from S3 bucket.py](Load%20data%20from%20S3%20bucket.py)

This small project retrieves a customer file from secure cloud storage, reads
it into a table, and shows a record count and sample rows as a quick check.
The file location and access settings are kept outside the code so private
details are not exposed in the project.

**What this demonstrates:** working with customer data, connecting to a cloud
file source, following basic data security practices, and checking that data
was loaded correctly.

## Tools Used

Python, pandas, Jupyter notebooks, charts, MySQL, and cloud file storage.

## How to Review the Work

Start with the online sales analysis for the clearest business story. Then
review the customer and sales pipeline to see how I prepare reliable data. The
passenger project shows how I organize data, and the cloud storage project
shows how I bring an external customer file into the analysis process.
