import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil
from datetime import datetime, timedelta
import random  # Added for random user agent selection
from dateutil.relativedelta import relativedelta

# Generate log file name with date and time
log_filename = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# Configure logging
logging.basicConfig(
    filename=log_filename,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def log_and_print(message):
    print(message)
    logging.info(message)
    

# Define 15 user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
]

def wait_for_element(driver, xpath, timeout=50):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def extract_and_save(driver, element_xpath, folder_path, file_name):
    try:
        driver.find_element(By.XPATH, element_xpath).click()
        time.sleep(1)

        html_element = driver.find_element(By.CLASS_NAME, "tabcontainer")
        table_text = html_element.text

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(table_text)
            log_and_print(f"extracting {file_name}")
    except Exception as e:
       print(f"Error extracting {file_name}")


def wait_for_download_completion(download_folder, timeout=60):
    """Waits dynamically for the download to complete by checking for .crdownload/.part files."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_folder)
        if any(file.endswith(".crdownload") or file.endswith(".part") for file in files):
            time.sleep(1)  # Wait a bit and check again
        else:
            return True  # Download is complete
    log_and_print("Warning: Download did not complete within the timeout period.")
    return False


def move_downloaded_file(download_folder, target_folder):
    if wait_for_download_completion(download_folder):
        files = os.listdir(download_folder)
        files.sort(key=lambda x: os.path.getctime(os.path.join(download_folder, x)), reverse=True)

        if files:
            latest_file = os.path.join(download_folder, files[0])  # Get the latest file
            shutil.move(latest_file, target_folder)
            log_and_print(f"Moved file to {target_folder}")
    else:
        log_and_print("Download did not complete, skipping move operation.")


from datetime import datetime
from dateutil.relativedelta import relativedelta

def increment_date_range(start_date, end_date):
    """Increment date range by one month accurately"""
    start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
    end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")

    # Increment by one month
    new_start_date = start_date_obj + relativedelta(months=1)
    new_end_date = end_date_obj + relativedelta(months=1)

    return new_start_date.strftime("%d/%m/%Y"), new_end_date.strftime("%d/%m/%Y")


# User inputs
start_date = input("Enter start date (DD/MM/YYYY): ")
end_date = input("Enter end date (DD/MM/YYYY): ")
start_page = int(input("Enter the page number to start from: "))
start_result = int(input("Enter the result number to start from: "))
count = int(input("Enter the number of months to end the loop: "))

log_and_print(f"start_date = {start_date}")
log_and_print(f"end_date = {end_date}")
log_and_print(f"start_page = {start_page}")
log_and_print(f"start_result = {start_result}")
log_and_print(f"Month_count = {count}")

# Loop while count is less than or equal to 5
while count <= 180:

    # Initialize WebDriver options
    formatted_download_path = f"{start_date.replace('/', '')} to {end_date.replace('/', '')}"
    download_path = os.path.abspath(formatted_download_path)
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    options = webdriver.EdgeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    })

    driver = webdriver.Edge(options=options)

    #Select a random user agent from the list and add it to the options
    selected_user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={selected_user_agent}')

    driver.get("https://planning.adur-worthing.gov.uk/online-applications/search.do?action=advanced")###URL
    log_and_print("logging https://planning.adur-worthing.gov.uk/online-applications/search.do?action=advanced")###URL
    time.sleep(2)

    log_and_print("Inputing Dates and Search")
    
    # Input date range
    driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[1]/input").send_keys(start_date)###Start Date
    driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[2]/input").send_keys(end_date)###End Date
    driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[4]/input[2]").click()###Search

    time.sleep(2)
    log_and_print("Arrenging Page for extraction")
    # Set results per page
    dropdown = driver.find_element(By.ID, "resultsPerPage")###per page set to 100
    dropdown.send_keys("100")
    driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/input[4]").click()###per page set to 100

    time.sleep(3)

    # Initialize page number before loop starts
    page_number = start_page  

    while True:
        log_and_print(f"Processing page {page_number}...")

        try:
            if page_number > 1:
                for _ in range(page_number - 1):
                    next_page_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
                    )
                    next_page_button.click()
                    time.sleep(1)
        except Exception:
            log_and_print("Reached last available page or invalid start page.")
            break


        i = start_result
        while i <= 101:
            try:
                log_and_print(f"Processing Result {i}... of Page {page_number}")
                result_xpath = f"/html/body/div/div/div[3]/div[3]/div[3]/div[1]/ul/li[{i}]/a"### Result
                result_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, result_xpath))
                )
                result_element.click()
                element = wait_for_element(driver, "/html/body/div/div/div[3]/div[3]/div[3]/table/tbody/tr[1]/td", 10)### Name for Subfolder
                result_name = ''.join(c for c in element.text if c.isalnum() or c in (' ', '_', '-')).strip()

                time.sleep(1)
                subFolderPath = os.path.join(download_path, result_name)
                if not os.path.exists(subFolderPath):
                    os.makedirs(subFolderPath)

                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/div[3]/table", subFolderPath, "Summary.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[2]/a", subFolderPath, "Further Information.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[3]/a", subFolderPath, "Contacts.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[4]/a", subFolderPath, "Important Dates.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[2]/a", subFolderPath, "Comments.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[5]/a", subFolderPath, "Related Cases.txt")###
                extract_and_save(driver, "/html/body/div/div/div[3]/div[3]/ul/li[3]/a", subFolderPath, "Constraints.txt")###

                # Handle Document Download
                download_button = wait_for_element(driver, "/html/body/div/div/div[3]/div[3]/ul/li[4]/a", 50)### Document
                download_button.click()
                time.sleep(1)

                doc_download_link = wait_for_element(driver, "/html/body/div/div/div[3]/div[3]/div[3]/p/a", 50)### Download Document
                doc_download_link.click()
                time.sleep(1)

                driver.switch_to.window(driver.window_handles[-1])
                print("Switched to new window: ", driver.title)

                select_element = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[1]/label/select", 50)### set to 100 for download Items
                select_element.send_keys("100")

                time.sleep(2)
                download_area = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[3]", 10)### Selectall
                if "Showing 0 to 0 of 0 entries" not in download_area.text:
                    select_all = driver.find_element(By.ID, "selectAll")
                    select_all.click()
                    time.sleep(2)
                    download_link = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[4]/a", 10)### Download Link
                    download_link.click()
                    time.sleep(10)

                
                move_downloaded_file(download_path, subFolderPath)
                log_and_print("Download completed. Moving file to subfolder.")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/ul/li[1]/a").click()### Back to Page
                time.sleep(1)

                i += 1

                if i > 100:
                    try:
                        next_page_button = driver.find_element(By.LINK_TEXT, "Next")### Next Page
                        next_page_button.click()
                        page_number += 1
                        i = 1
                        start_result = 1  # Restart loop from 1 on the new page
                        time.sleep(3)
                    except Exception:
                        log_and_print("No more pages available.")
                        break
                    
            except Exception:
                log_and_print("No more results on this page or an error occurred.")
                break

    driver.quit()
    start_date, end_date = increment_date_range(start_date, end_date)
    log_and_print(f"Scraping range {start_date} to {end_date}")
    i = 1
    start_result = 1
    start_page = 1
    
log_and_print("Data extraction completed.")
