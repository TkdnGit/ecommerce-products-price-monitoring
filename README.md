
Flipkart Price Monitoring System

A Python + Selenium based Flipkart product price monitoring system that collects product information every time the program is run and maintains historical price and availability data.

Features

Reads Flipkart product information from products.csv

Supports multiple products

Opens each product URL using Selenium

Extracts:

Product ID

Product Name

Brand

Price

Rating

Availability

Scrape Date

Scrape Time

Product URL

Automatically scrolls the product page

Maintains historical price data in CSV format

Calculates:

Previous Price

Price Change

Price Change Percentage

Creates a latest-status report for each product

Detects availability changes

Generates an Excel report with multiple worksheets

Runs immediately when the Python program starts

No fixed schedule.

Project Structure

Flipkart-Price-Monitoring/
│
├── flipkart_price_monitor.py
├── products.csv
├── requirements.txt
├── README.md
│
├── data/
│   └── price_history.csv
│
└── reports/
    └── Flipkart_Price_Monitoring_Report.xlsx

Input File

The program expects a file named:

products.csv

The CSV must contain these columns:

Product_ID,Product_Name,Platform,URL

Example:

Product_ID,Product_Name,Platform,URL
P001,TRIGGR UltraBuds N5,Flipkart,https://www.flipkart.com/...
P002,Myxes New TWS M19 Gaming Earbuds,Flipkart,https://www.flipkart.com/...

Only rows where Platform is Flipkart are processed.

Installation

1. Clone or download the project

Open PowerShell or Command Prompt and go to the project folder.

2. Create a virtual environment (recommended)

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

Run the Program

Run:

python flipkart_price_monitor.py

The program starts scraping immediately.

There is:

No scheduler

No fixed  execution time

No need to wait for a scheduled time

Every time the script is executed, a new price-monitoring record is collected.

Output Files

1. Price History

The historical data is saved to:

data/price_history.csv

This file stores data from previous runs and the current run.

Typical columns include:

Product_ID
Product_Name
Brand
Price
Rating
Availability
Scrape_Date
Scrape_Time
Product_URL

2. Excel Report

The Excel report is saved to:

reports/Flipkart_Price_Monitoring_Report.xlsx

The report contains four worksheets:

Price_History

Contains historical product records together with:

Previous_Price

Price_Change

Price_Change_Percent

Latest_Status

Contains the latest scraped status for each product.

Price_Changes

Contains records where a previous price exists, allowing price changes to be reviewed.

Availability_Changes

Shows changes between the previous and current availability status.

Price Change Calculation

The system calculates:

Price Change = Current Price - Previous Price

and:

Price Change % =
(Current Price - Previous Price)
/
Previous Price
× 100

For example, if the previous price is ₹1,500 and the current price is ₹1,300:

Price Change = 1300 - 1500
             = -200

So the price decreased by ₹200.

Availability Monitoring

The script checks the page text for common availability indicators.

In Stock

Examples:

Add to Cart
Buy Now

Out of Stock

Examples:

Out of Stock
Currently Unavailable
Sold Out

If neither condition is detected, the status is:

Unknown

Browser Automation

The project uses Selenium with Chrome.

ChromeDriver is automatically managed using:

webdriver-manager

Therefore, a compatible ChromeDriver does not need to be manually downloaded and configured.

Important Notes

The Flipkart page structure can change over time. If Flipkart changes its HTML/CSS structure, XPath locators may need to be updated.

Product pages should be publicly accessible to Selenium.

Scraping results may vary depending on page loading, network conditions, and website behavior.

The script includes delays and scrolling to allow dynamic page content to load.

The script closes Chrome automatically after the monitoring run finishes.

Portfolio Use

This project demonstrates practical skills in:

Python

Selenium Web Scraping

Pandas

XPath

Dynamic web-page handling

Data cleaning

Historical data management

Price-change analysis

Availability monitoring

CSV data storage

Excel report generation

Automated browser control

Technology Stack

Python

Selenium

Pandas

OpenPyXL

WebDriver Manager

Google Chrome

Disclaimer

This project is intended for educational and portfolio purposes. Use web scraping responsibly and respect the target website's terms, robots.txt, access controls, and applicable laws.
