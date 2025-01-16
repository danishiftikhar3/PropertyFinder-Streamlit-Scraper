from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def test_chromedriver():
    """
    Test if ChromeDriver is set up correctly.
    Launches a test browser, retrieves the browser version, and confirms communication.
    """
    try:
        # Configure Chrome options for testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(), options=chrome_options)

        # Access a test page
        driver.get("https://www.google.com")

        # Retrieve and print Chrome and ChromeDriver versions
        browser_version = driver.capabilities["browserVersion"]
        driver_version = driver.capabilities["chrome"]["chromedriverVersion"].split(
            " "
        )[0]

        print(f"Chrome Browser Version: {browser_version}")
        print(f"ChromeDriver Version: {driver_version}")

        # Close the browser
        driver.quit()

        # Verify versions match
        if not browser_version.startswith(driver_version.split(".")[0]):
            print("Warning: Mismatch between Chrome and ChromeDriver versions!")
        else:
            print(
                "Success: ChromeDriver is properly set up and matches the browser version."
            )

    except WebDriverException as e:
        print(f"WebDriverException: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_chromedriver()
