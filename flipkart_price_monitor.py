# ============================================================
# FLIPKART PRICE MONITORING SYSTEM
# ============================================================

# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

import time
import random
import os
import re
from datetime import datetime


# ============================================================
# 2. FILE / DIRECTORY SETTINGS
# ============================================================

INPUT_FILE = "products.csv"

DATA_DIR = "data"
REPORT_DIR = "reports"

HISTORY_FILE = os.path.join(
    DATA_DIR,
    "price_history.csv"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "Flipkart_Price_Monitoring_Report.xlsx"
)


# ============================================================
# 3. CREATE DIRECTORIES
# ============================================================

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ============================================================
# 4. CREATE SELENIUM DRIVER
# ============================================================

def create_driver():

    options = Options()

    # আপনার original scraping code-এর settings
    options.add_argument("--lang=en-US")

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    options.add_argument(
        "--disable-info-bars"
    )

    options.add_argument(
        "--disable-extensions"
    )

    driver = webdriver.Chrome(
        options=options,
        service=Service(
            ChromeDriverManager().install()
        )
    )

    return driver


# ============================================================
# 5. LOAD PRODUCTS.CSV
# ============================================================

def load_products():

    print("\n======================================")
    print("LOADING PRODUCTS.CSV")
    print("======================================")

    if not os.path.exists(INPUT_FILE):

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    products = pd.read_csv(
        INPUT_FILE
    )

    required_columns = [
        "Product_ID",
        "Product_Name",
        "Platform",
        "URL"
    ]

    # Check required columns
    for column in required_columns:

        if column not in products.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )

    # Only Flipkart products
    products = products[
        products["Platform"]
        .astype(str)
        .str.lower()
        .eq("flipkart")
    ].copy()

    # Remove empty URLs
    products = products[
        products["URL"].notna()
    ]

    products = products[
        products["URL"]
        .astype(str)
        .str.strip()
        != ""
    ]

    print(
        f"Products loaded: {len(products)}"
    )

    return products


# ============================================================
# 6. AUTO SCROLL
# ============================================================

def auto_scroll(driver):

    try:

        l_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        for i in range(
            0,
            l_height,
            300
        ):

            driver.execute_script(
                f"window.scrollTo(0, {i});"
            )

            time.sleep(
                random.uniform(
                    0.3,
                    0.8
                )
            )

            n_height = driver.execute_script(
                "return document.body.scrollHeight"
            )

            if n_height != l_height:

                l_height = n_height

    except Exception:

        pass


# ============================================================
# 7. CLEAN PRICE
# ============================================================

def clean_price(price_text):

    if not price_text:

        return None

    try:

        price_text = str(
            price_text
        )

        # ₹1,299 -> ₹1299
        price_text = price_text.replace(
            ",",
            ""
        )

        match = re.search(
            r"(\d+(?:\.\d+)?)",
            price_text
        )

        if match:

            return float(
                match.group(1)
            )

    except Exception:

        pass

    return None


# ============================================================
# 8. EXTRACT PRICE
# ============================================================

def extract_price(driver):

    price = None

    # --------------------------------------------------------
    # PRIMARY PRICE XPATH
    # --------------------------------------------------------

    try:

        price_element = driver.find_element(
            By.XPATH,
            "(//div[contains(text(),'₹')])[6]"
        )

        price = clean_price(
            price_element.text
        )

    except Exception:

        pass


    # --------------------------------------------------------
    # BACKUP PRICE LOCATOR
    # --------------------------------------------------------

    if price is None:

        try:

            price_elements = driver.find_elements(
                By.XPATH,
                "//div[contains(text(),'₹')]"
            )

            for element in price_elements:

                text = element.text.strip()

                if "₹" in text:

                    value = clean_price(
                        text
                    )

                    if value is not None:

                        price = value

                        break

        except Exception:

            pass


    return price


# ============================================================
# 9. EXTRACT PRODUCT NAME
# ============================================================

def extract_product_name(driver):

    try:

        name = driver.find_element(
            By.XPATH,
            "//h1"
        ).text.strip()

        return name

    except Exception:

        return ""


# ============================================================
# 10. EXTRACT RATING
# ============================================================

def extract_rating(driver):

    try:

        rating_element = driver.find_element(
            By.XPATH,
            "(//div[@dir='auto' and @class='css-146c3p1'])[1]"
        )

        rating = rating_element.text.strip()

        if re.match(
            r"^[0-5](\.\d)?$",
            rating
        ):

            return rating

    except Exception:

        pass

    return ""


# ============================================================
# 11. EXTRACT AVAILABILITY
# ============================================================

def extract_availability(driver):

    try:

        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower()

    except Exception:

        return "Unknown"


    # --------------------------------------------------------
    # OUT OF STOCK
    # --------------------------------------------------------

    out_of_stock_words = [
        "out of stock",
        "currently unavailable",
        "sold out"
    ]

    for word in out_of_stock_words:

        if word in page_text:

            return "Out of Stock"


    # --------------------------------------------------------
    # IN STOCK
    # --------------------------------------------------------

    available_words = [
        "add to cart",
        "buy now"
    ]

    for word in available_words:

        if word in page_text:

            return "In Stock"


    return "Unknown"


# ============================================================
# 12. EXTRACT BRAND
# ============================================================

def extract_brand(driver):    

    try:
        driver.execute_script("window.scrollTo(0, 600);")
        all_details = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(text(),'All details')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", all_details[0])
                
        # driver.execute_script("arguments[0].click();",all_details[0])
        specification = driver.find_element(By.XPATH, "//div[contains(text(),'Specification')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", specification)
        driver.execute_script("arguments[0].click();",specification)
        time.sleep(random.uniform(1.5, 5.5))
        try:
            brand = driver.find_element(By.XPATH,"(//div[contains(.,'Brand')]/following::div[1])[1]").text
            time.sleep(random.uniform(2.5, 4.5))
        except:
            brand = ""        

    except Exception:
        pass      
    return brand


# ============================================================
# 13. SCRAPE ONE PRODUCT
# ============================================================

def scrape_product(
    driver,
    product_id,
    product_name,
    product_url
):

    print("\n--------------------------------------")

    print(
        f"Product ID   : {product_id}"
    )

    print(
        f"Product Name : {product_name}"
    )

    print(
        f"URL          : {product_url}"
    )

    print("--------------------------------------")


    # --------------------------------------------------------
    # OPEN PRODUCT PAGE
    # --------------------------------------------------------

    driver.get(
        product_url
    )

    time.sleep(
        random.uniform(
            2.5,
            4.5
        )
    )


    # --------------------------------------------------------
    # AUTO SCROLL
    # --------------------------------------------------------

    auto_scroll(
        driver
    )


    # --------------------------------------------------------
    # PRODUCT NAME
    # --------------------------------------------------------

    scraped_name = extract_product_name(
        driver
    )

    if not scraped_name:

        scraped_name = product_name


    # --------------------------------------------------------
    # RATING
    # --------------------------------------------------------

    rating = extract_rating(
        driver
    )


    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price = extract_price(
        driver
    )


    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    availability = extract_availability(
        driver
    )


    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    brand = extract_brand(
        driver
    )


    # --------------------------------------------------------
    # DATE / TIME
    # --------------------------------------------------------

    scrape_datetime = datetime.now()

    scrape_date = scrape_datetime.strftime(
        "%Y-%m-%d"
    )

    scrape_time = scrape_datetime.strftime(
        "%H:%M:%S"
    )


    # --------------------------------------------------------
    # PRODUCT RESULT
    # --------------------------------------------------------

    product_data = {

        "Product_ID":
            product_id,

        "Product_Name":
            scraped_name,

        "Brand":
            brand,

        "Price":
            price,

        "Rating":
            rating,

        "Availability":
            availability,

        "Scrape_Date":
            scrape_date,

        "Scrape_Time":
            scrape_time,

        "Product_URL":
            product_url
    }


    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print(
        f"Price        : {price}"
    )

    print(
        f"Rating       : {rating}"
    )

    print(
        f"Availability : {availability}"
    )

    print(
        f"Brand        : {brand}"
    )


    return product_data


# ============================================================
# 14. LOAD OLD HISTORY
# ============================================================

def load_history():

    if os.path.exists(
        HISTORY_FILE
    ):

        try:

            history = pd.read_csv(
                HISTORY_FILE
            )

            print(
                f"\nPrevious history loaded: "
                f"{len(history)} records"
            )

            return history

        except Exception:

            pass

    return pd.DataFrame()


# ============================================================
# 15. SAVE HISTORY
# ============================================================

def save_history(
    new_records
):

    new_df = pd.DataFrame(
        new_records
    )

    old_df = load_history()


    # --------------------------------------------------------
    # COMBINE OLD + NEW
    # --------------------------------------------------------

    if not old_df.empty:

        history = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )

    else:

        history = new_df.copy()


    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    history.to_csv(
        HISTORY_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nHistory saved: "
        f"{HISTORY_FILE}"
    )

    return history


# ============================================================
# 16. CREATE PRICE CHANGES
# ============================================================

def create_price_changes(
    history
):

    if history.empty:

        return pd.DataFrame()


    history = history.copy()


    # Sort by product + date + time
    history = history.sort_values(
        [
            "Product_ID",
            "Scrape_Date",
            "Scrape_Time"
        ]
    )


    # --------------------------------------------------------
    # PREVIOUS PRICE
    # --------------------------------------------------------

    history[
        "Previous_Price"
    ] = (
        history
        .groupby(
            "Product_ID"
        )["Price"]
        .shift(1)
    )


    # --------------------------------------------------------
    # PRICE CHANGE
    # --------------------------------------------------------

    history[
        "Price_Change"
    ] = (
        history["Price"]
        -
        history["Previous_Price"]
    )


    # --------------------------------------------------------
    # PRICE CHANGE %
    # --------------------------------------------------------

    history[
        "Price_Change_Percent"
    ] = (
        history["Price_Change"]
        /
        history["Previous_Price"]
        *
        100
    )


    # --------------------------------------------------------
    # DIVISION BY ZERO
    # --------------------------------------------------------

    history.loc[
        history["Previous_Price"] == 0,
        "Price_Change_Percent"
    ] = None


    return history


# ============================================================
# 17. CREATE LATEST STATUS
# ============================================================

def create_latest_status(
    history
):

    if history.empty:

        return pd.DataFrame()


    latest = (
        history
        .sort_values(
            [
                "Product_ID",
                "Scrape_Date",
                "Scrape_Time"
            ]
        )
        .groupby(
            "Product_ID",
            as_index=False
        )
        .tail(1)
    )


    latest = latest[
        [
            "Product_ID",
            "Product_Name",
            "Brand",
            "Price",
            "Rating",
            "Availability",
            "Scrape_Date",
            "Scrape_Time",
            "Product_URL"
        ]
    ]


    return latest


# ============================================================
# 18. CREATE AVAILABILITY CHANGES
# ============================================================

def create_availability_changes(
    history
):

    if history.empty:

        return pd.DataFrame()


    df = history.copy()


    df = df.sort_values(
        [
            "Product_ID",
            "Scrape_Date",
            "Scrape_Time"
        ]
    )


    # --------------------------------------------------------
    # PREVIOUS AVAILABILITY
    # --------------------------------------------------------

    df[
        "Previous_Availability"
    ] = (
        df
        .groupby(
            "Product_ID"
        )["Availability"]
        .shift(1)
    )


    # --------------------------------------------------------
    # AVAILABILITY CHANGED
    # --------------------------------------------------------

    df[
        "Availability_Changed"
    ] = (
        df["Availability"]
        !=
        df["Previous_Availability"]
    )


    # First record has no previous status
    df = df[
        df["Previous_Availability"]
        .notna()
    ]


    return df[
        [
            "Product_ID",
            "Product_Name",
            "Scrape_Date",
            "Scrape_Time",
            "Previous_Availability",
            "Availability",
            "Availability_Changed"
        ]
    ]


# ============================================================
# 19. CREATE EXCEL REPORT
# ============================================================

def create_report(
    history
):

    print(
        "\nCreating Excel report..."
    )


    # --------------------------------------------------------
    # PRICE HISTORY
    # --------------------------------------------------------

    price_history = create_price_changes(
        history
    )


    # --------------------------------------------------------
    # LATEST STATUS
    # --------------------------------------------------------

    latest_status = create_latest_status(
        history
    )


    # --------------------------------------------------------
    # AVAILABILITY CHANGES
    # --------------------------------------------------------

    availability_changes = (
        create_availability_changes(
            history
        )
    )


    # --------------------------------------------------------
    # SAVE EXCEL
    # --------------------------------------------------------

    with pd.ExcelWriter(
        REPORT_FILE,
        engine="openpyxl"
    ) as writer:

        # Sheet 1
        price_history.to_excel(
            writer,
            sheet_name="Price_History",
            index=False
        )


        # Sheet 2
        latest_status.to_excel(
            writer,
            sheet_name="Latest_Status",
            index=False
        )


        # Sheet 3
        price_history[
            price_history[
                "Previous_Price"
            ].notna()
        ].to_excel(
            writer,
            sheet_name="Price_Changes",
            index=False
        )


        # Sheet 4
        availability_changes.to_excel(
            writer,
            sheet_name="Availability_Changes",
            index=False
        )


    print(
        f"Report saved: "
        f"{REPORT_FILE}"
    )


# ============================================================
# 20. MAIN PRICE MONITORING FUNCTION
# ============================================================

def run_price_monitoring():

    print("\n")
    print("=" * 70)
    print(
        "FLIPKART PRICE MONITORING SYSTEM"
    )
    print("=" * 70)


    print(
        "Run time:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    print("=" * 70)


    driver = None

    new_records = []


    try:

        # ----------------------------------------------------
        # LOAD PRODUCTS.CSV
        # ----------------------------------------------------

        products = load_products()


        # ----------------------------------------------------
        # CREATE CHROME DRIVER
        # ----------------------------------------------------

        print(
            "\nStarting Chrome..."
        )

        driver = create_driver()


        # ----------------------------------------------------
        # SCRAPE EACH PRODUCT
        # ----------------------------------------------------

        for _, product in products.iterrows():

            try:

                result = scrape_product(

                    driver,

                    product["Product_ID"],

                    product["Product_Name"],

                    product["URL"]

                )


                new_records.append(
                    result
                )


                # Delay between products
                time.sleep(
                    random.uniform(
                        2.0,
                        4.0
                    )
                )


            except Exception as e:

                print(
                    f"\nError scraping "
                    f"{product['Product_ID']}: {e}"
                )

                continue


        # ----------------------------------------------------
        # SAVE HISTORY + CREATE REPORT
        # ----------------------------------------------------

        if new_records:

            history = save_history(
                new_records
            )


            create_report(
                history
            )


        else:

            print(
                "\nNo product data scraped."
            )


    except Exception as e:

        print(
            f"\nSYSTEM ERROR: {e}"
        )


    finally:

        # ----------------------------------------------------
        # CLOSE CHROME
        # ----------------------------------------------------

        if driver:

            driver.quit()


    print("\n")
    print("=" * 70)
    print(
        "PRICE MONITORING RUN COMPLETED"
    )
    print("=" * 70)


# ============================================================
# 21. RUN IMMEDIATELY
# ============================================================
# ============================================================

run_price_monitoring()