from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import requests

# Define website and paths
website = 'https://assessmentonline.naac.gov.in/public/index.php/hei_dashboard'
path = r'C:\Users\Admin\Desktop\chromedriver-win64\chromedriver-win64\chromedriver.exe'
download_dir = r"C:\Users\Admin\Desktop\scraped_data"

# Create download directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Test if writing to the directory is permitted
test_file_path = os.path.join(download_dir, "test_permission.txt")
try:
    with open(test_file_path, "w") as test_file:
        test_file.write("Test")
    os.remove(test_file_path)
    print("Permission to write to the directory is confirmed.")
except Exception as e:
    print(f"Permission to write to the directory is denied. Error: {e}")
    exit(1)

# Set Chrome options
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize WebDriver
service = Service(path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the website
    driver.get(website)
    print("Website opened successfully.")

    # Interact with dropdowns
    select = Select(driver.find_element(By.ID, "inst_type"))
    select.select_by_visible_text("University")

    select = Select(driver.find_element(By.ID, "state"))
    select.select_by_visible_text("Maharashtra")

    select = Select(driver.find_element(By.ID, "iiqa_status"))
    select.select_by_visible_text("Result Declared")

    # Click the Show button
    show_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "showbtn"))
    )
    driver.execute_script("arguments[0].click();", show_button)
    print("Show button clicked.")

    # Wait for the table to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )
    print("Table loaded.")

    # Process the first 5 colleges
    view_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'View')]")[:5]
    for index, view_button in enumerate(view_buttons, start=1):
        print(f"Processing College {index}...")
        view_button.click()

        # Wait for the SSR Information link
        ssr_link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "SSR Information"))
        )
        ssr_link.click()

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'ssr_report')]"))
        )

        # Download the file
        download_button = driver.find_element(By.XPATH, "//a[contains(@href, 'ssr_report')]")
        file_url = download_button.get_attribute("href")
        print(f"Downloading file from URL: {file_url}")

        # Download the file using requests
        headers = {"User-Agent": "Mozilla/5.0"}
        file_response = requests.get(file_url, headers=headers)

        if file_response.status_code == 200:
            file_name = os.path.join(download_dir, f"college_{index}.pdf")  # Change extension if needed
            with open(file_name, "wb") as file:
                file.write(file_response.content)
            print(f"Downloaded file: {file_name}")
        else:
            print(f"Failed to download file for College {index}. Status: {file_response.status_code}")

        # Close the current tab and return to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    print("Download completed for top 5 colleges.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
