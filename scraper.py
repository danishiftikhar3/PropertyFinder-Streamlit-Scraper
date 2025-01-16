import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import math
import time


# Define scraper function
def scrape_page(url, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "property-card-module_property-card__wrapper__ZZTal")
        )
    )
    print("no error here 24")
    listings = driver.find_elements(
        By.CLASS_NAME, "property-card-module_property-card__wrapper__ZZTal"
    )
    return [
        {"url": url, "html_content": listing.get_attribute("outerHTML")}
        for listing in listings
    ]


# Extract data from HTML
def extract_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    property_type_elem = soup.find(
        "p", class_="styles-module_content__property-type__QuVl4"
    )
    price_elem = soup.find("p", class_="styles-module_content__price__SgQ5p")
    title_elem = soup.find("h2", class_="styles-module_content__title__eOEkd")
    broker_logo_elem = soup.find(
        "div", class_="styles-module_content__broker-logo__6-u-9"
    )
    location_elem = soup.find(
        "div", class_="styles-module_content__location-container__pRGhf"
    )
    bedrooms_elem = soup.find("p", {"data-testid": "property-card-spec-bedroom"})
    bathrooms_elem = soup.find("p", {"data-testid": "property-card-spec-bathroom"})
    area_elem = soup.find("p", {"data-testid": "property-card-spec-area"})

    property_type = property_type_elem.text.strip() if property_type_elem else None
    price = price_elem.text.strip() if price_elem else None
    title = title_elem.text.strip() if title_elem else None
    broker_logo_url = broker_logo_elem.find("img")["src"] if broker_logo_elem else None
    location = location_elem.find("p").text.strip() if location_elem else None
    bedrooms = bedrooms_elem.text.strip() if bedrooms_elem else None
    bathrooms = bathrooms_elem.text.strip() if bathrooms_elem else None
    area = area_elem.text.strip() if area_elem else None

    return (
        property_type,
        price,
        title,
        broker_logo_url,
        location,
        bedrooms,
        bathrooms,
        area,
    )


# Main scraper logic
def main():
    # Load configuration
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"Configuration file '{config_file}' not found.")
        print(
            "Please create a 'config.json' file with 'url' and 'total_listings' keys."
        )
        return

    with open(config_file, "r") as f:
        config = json.load(f)

    url = config.get("url")
    total_listings = config.get("total_listings")

    if not url or not total_listings:
        print(
            "Invalid configuration. Ensure 'url' and 'total_listings' are specified in 'config.json'."
        )
        return

    # Calculate number of pages to scrape (assuming 25 listings per page)
    n = math.ceil(total_listings / 25)

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows OS
    chrome_options.add_argument(
        "--window-size=1920x1080"
    )  # Set the window size for headless mode

    # Initialize WebDriver with options
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    all_listings = []

    try:
        print(f"Scraping {n} pages... This may take a while.")
        for i in range(1, n + 1):
            paginated_url = f"{url}&page={i}"
            print(f"Scraping page {i} of {n}...")
            listings = scrape_page(paginated_url, driver)
            print(listings)
            all_listings.extend(listings)
            time.sleep(0.1)  # Small delay between requests

        driver.quit()

        if all_listings:
            # Extract data and save to DataFrame
            df = pd.DataFrame(all_listings)
            df[
                "property_type",
                "price",
                "title",
                "broker_logo_url",
                "location",
                "bedrooms",
                "bathrooms",
                "area",
            ] = zip(*df["html_content"].apply(extract_data))

            # Save to CSV
            output_file = "results.csv"
            df.to_csv(output_file, index=False)
            print(f"Scraping completed successfully! Data saved to '{output_file}'.")
        else:
            print("No data to export. Scraping did not collect any listings.")

    except Exception as e:
        print(f"Error occurred: {e}")
        driver.quit()


if __name__ == "__main__":
    main()
