import logging
import time
import os
import shutil
import sys
import random  # Added for random user agent selection
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains  # Mouse movement
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium_stealth import stealth

def setup_stealth_edge():
    """Sets up an undetected Edge WebDriver with stealth mode."""
    driver = uc.Chrome(
        browser_executable_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    )

    # Apply Selenium Stealth to avoid detection
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    return driver

def is_driver_alive(driver):
    """Check if the WebDriver is still running."""
    try:
        driver.window_handles  # Try to access an attribute
        return True
    except:
        log_and_print("Browser is closed. Stopping execution.")
        return False



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

def move_mouse_and_scroll(driver, element):
    """Moves the mouse to a given element with random offsets and scrolls randomly."""
    try:
        action = ActionChains(driver)

        # Random small offsets to avoid detection
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-5, 5)

        # Move the mouse with offset
        action.move_to_element_with_offset(element, x_offset, y_offset).perform()
        time.sleep(random.uniform(0.5, 1.5))  # Human-like delay

        # Scroll randomly up/down
        scroll_direction = random.choice([Keys.ARROW_DOWN, Keys.ARROW_UP])
        scroll_times = random.randint(1, 3)  # Number of times to scroll

        for _ in range(scroll_times):
            action.send_keys(scroll_direction).perform()
            time.sleep(random.uniform(0.5, 1))  # Small delay between scrolls

    except Exception as e:
        print(f"Mouse movement and scrolling failed: {e}")

        
def wait_for_element(driver, xpath, timeout=50):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def extract_and_save(driver, element_xpath, folder_path, file_name):
    try:
        # Check if the driver is still open by attempting a simple command
        if driver is None or driver.service.process is None:
            log_and_print(f"Error: WebDriver is closed. Cannot extract {file_name}.")
            sys.exit()  # Immediately exit the entire script
        
        element = driver.find_element(By.XPATH, element_xpath)  # Find the element first
        move_mouse_and_scroll(driver, element)  # Pass the element instead of XPath

        element.click()  # Click after moving and scrolling
        time.sleep(1)

        html_element = driver.find_element(By.CLASS_NAME, "tabcontainer")
        table_text = html_element.text

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(table_text)
        
        log_and_print(f"Successfully extracted and saved {file_name}")
    
    except Exception as e:
        log_and_print(f"Error extracting {file_name}: {str(e)}")



def wait_for_download_completion(download_folder, timeout=60):
    """Waits dynamically for the download to complete by checking for .crdownload/.part files."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_folder)
        if any(file.endswith(".crdownload") or file.endswith(".part") for file in files):
            time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds 
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
import os

def delete_zip_and_rar_files(download_folder):
    """Deletes all .zip and .rar files from the specified download directory."""
    try:
        if not os.path.exists(download_folder):
            print(f"Error: Path '{download_folder}' does not exist.")
            return
        
        files_deleted = 0
        for file_name in os.listdir(download_folder):
            if file_name.endswith((".zip", ".rar")):
                file_path = os.path.join(download_path, file_name)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
                files_deleted += 1

        if files_deleted == 0:
            print("No ZIP or RAR files found.")
        else:
            print(f"Deleted {files_deleted} files successfully.")

    except Exception as e:
        print(f"Error deleting files: {e}")



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

# Function to retry extraction logic with exponential backoff
def retry_with_backoff(func, *args, max_attempts=5, base_delay=60):
    """Retries a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func(*args)
        except Exception as e:
            log_and_print(f"Attempt {attempt + 1} failed: {e}")
            wait_time = base_delay * (2 ** attempt)
            log_and_print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    log_and_print("Max retry attempts reached. Skipping this step.")

    
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

    

    #Select a random user agent from the list and add it to the options
    selected_user_agent = random.choice(user_agents)
    #options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    #options.add_argument("--disable-gpu")  # Fixes rendering issues in headless mode
    #driver.add_argument("--log-level=3")  # Suppresses logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disables DevTools logs
    #driver.add_argument("--disable-extensions")  # Prevents extensions from interfering
    options.add_argument(f'user-agent={selected_user_agent}')

    
    driver = webdriver.Edge(options=options)
    if __name__ == "__main__":
        driver.get("https://planning.adur-worthing.gov.uk/online-applications/search.do?action=advanced")###URL
        #driver.minimize_window()  # Hides the browser window
    else:
        log_and_print("Browser Crushed")
        
    log_and_print("logging https://planning.adur-worthing.gov.uk/online-applications/search.do?action=advanced")###URL
    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds

    log_and_print("Inputing Dates and Search")
    
    # Input date range
    retry_with_backoff(driver.find_element, By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[1]/input").send_keys(start_date)###Start Date
    retry_with_backoff(driver.find_element, By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[2]/input").send_keys(end_date)###End Date
    retry_with_backoff(driver.find_element, By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/div[4]/input[2]").click()###Search

    time.sleep(2)
    log_and_print("Arrenging Page for extraction")
    # Set results per page
    dropdown = driver.find_element(By.ID, "resultsPerPage")###per page set to 100
    move_mouse_and_scroll(driver, dropdown)
    dropdown.send_keys("100")
    retry_with_backoff(driver.find_element, By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/form/input[4]").click()###per page set to 100

    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds

    # Initialize page number before loop starts
    page_number = start_page  

    while True:
        log_and_print(f"Processing page {page_number}...")
        if not is_driver_alive(driver):
            log_and_print(f"Error: Browser is closed. Stopping execution.")
            break  # Exit the loop if browser is closed

    
        try:
            if page_number > 1:
                for _ in range(page_number - 1):
                    next_page_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
                    )
                    next_page_button.click()
                    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
        except Exception:
            log_and_print("Reached last available page or invalid start page.")
            break


        i = start_result
        while i <= 101:
            if not is_driver_alive(driver):
                log_and_print(f"Error: Browser is closed. Stopping execution.")
                break  # Exit the loop if browser is closed

            try:
                if not is_driver_alive(driver):
                    log_and_print(f"Error: Browser is closed. Stopping execution.")
                    break  # Exit the loop if browser is closed
                
    
                log_and_print(f"Processing Result {i}... of Page {page_number}")
                result_xpath = f"/html/body/div/div/div[3]/div[3]/div[3]/div[1]/ul/li[{i}]/a"### Result
                result_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, result_xpath))
                )
                move_mouse_and_scroll(driver, result_element)
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


                if not driver: log_and_print("Exiting script due to browser crash.", "error")
                
                ###################################################################################### Handle Document Download
                download_button_xpath = "/html/body/div/div/div[3]/div[3]/ul/li[4]/a"
                download_button = wait_for_element(driver, download_button_xpath, 50)

                if download_button:
                    move_mouse_and_scroll(driver, download_button)
                    try:
                        download_button.click()
                        time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior
                        log_and_print("Download button clicked successfully.")
                    except Exception as e:
                        log_and_print(f"Failed to click download button: {e}")
                else:
                    log_and_print("Download button not found, skipping download process.")

                doc_download_link = wait_for_element(driver, "/html/body/div/div/div[3]/div[3]/div[3]/p/a", 50)### Download Document
                move_mouse_and_scroll(driver, doc_download_link)
                doc_download_link.click()
                time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds

               

                driver.switch_to.window(driver.window_handles[-1])
                print("Switched to new window: ", driver.title)
                time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
                 
                select_element = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[1]/label/select", 50)### set to 100 for download Items
                move_mouse_and_scroll(driver, select_element)
                select_element.send_keys("100")
                
                time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
                download_area = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[3]", 10) ### No of Downloads to check
                time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds

                if "Showing 0 to 0 of 0 entries" not in download_area.text:
                    delete_zip_and_rar_files(download_path)
                    select_all = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/table/thead/tr/th[1]/input", 10)  ### Selectall
                    move_mouse_and_scroll(driver, select_all)
                    select_all.click()
                    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
                    download_link = wait_for_element(driver, "/html/body/main/div[1]/div/div/div/div[4]/div[4]/a", 10)### Download Link
                    move_mouse_and_scroll(driver, download_link)
                    download_link.click()
                    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
        
                
                move_downloaded_file(download_path, subFolderPath)
                log_and_print("Download completed. Moving file to subfolder.")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                retry_with_backoff(driver.find_element, By.XPATH, "/html/body/div/div/div[3]/div[3]/div[2]/ul/li[1]/a").click()### Back to Page
                time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds

                 #####################################################################################
                
                i += 1

                if i > 100:
                    try:
                        next_page_button = driver.find_element(By.LINK_TEXT, "Next")### Next Page
                        
                        next_page_button.click()
                        page_number += 1
                        i = 1
                        start_result = 1  # Restart loop from 1 on the new page
                        time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
                    except Exception:
                        log_and_print("No more pages available.")
                        break
                    
            except Exception:
                log_and_print("No more results on this page or an error occurred.")
                break

    if not is_driver_alive(driver):
        log_and_print(f"Error: Browser is closed. Stopping execution.")
        break  # Exit the loop if browser is closed
    driver.quit()
    start_date, end_date = increment_date_range(start_date, end_date)
    log_and_print(f"Scraping range {start_date} to {end_date}")
    i = 1
    start_result = 1
    start_page = 1

    
    
log_and_print("Data extraction completed.")
