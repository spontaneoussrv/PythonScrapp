import logging
import re
import time
import os
import shutil
import math
import sys
import random  # Added for random user agent selection
import zipfile
import patoolib
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

#ALL Functions###########################################################################################################################################################

# Check Browser Open or Not
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

        

# Extract a table contents
def extract_and_save(driver, element_xpath, folder_path, file_name):
    try:
        # Check if the driver is still open by attempting a simple command
        if driver is None or driver.service.process is None:
            log_and_print(f"Error: WebDriver is closed. Cannot extract {file_name}.")
            sys.exit()  # Immediately exit the entire script
        
        element = driver.find_element(By.XPATH, element_xpath)  # Find the element first
        move_mouse_and_scroll(driver, element)  # Pass the element instead of XPath

        element.click()  # Click after moving and scrolling
        time.sleep(random.uniform(0.5, 1.5))

        html_element = driver.find_element(By.CLASS_NAME, "tabcontainer")
        table_text = html_element.text

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(table_text)
        
        log_and_print(f"Successfully extracted and saved {file_name}")
    
    except Exception as e:
        log_and_print(f"Error extracting {file_name}")

# Waiting for download to complete
def wait_for_download_completion(download_folder, timeout=300, check_interval=10, stability_checks=7):
    """Waits for a .crdownload or .zip/.rar file, monitors stability if needed, and confirms download completion."""
    start_time = time.time()
    last_sizes = {}
    stable_count = 0

    print(f"Monitoring {download_folder} for a .crdownload or .zip/.rar file to start the download...")

    # Step 1: Wait for a .crdownload or .zip/.rar file (5 minutes max)
    while time.time() - start_time < 300:  # 5 minutes
        files = os.listdir(download_folder)
        temp_files = [file for file in files if file.endswith(".crdownload")]
        archive_files = [file for file in files if file.endswith(".zip") or file.endswith(".rar")]

        if archive_files:
            print(f"[Step] Archive files detected: {archive_files}. Download already complete!")
            return True  # Download is already finished

        if temp_files:
            print(f"[Step] .crdownload file detected: {temp_files}. Starting stability monitoring.")
            break  # Proceed to stability monitoring
        else:
            print("[Step] No .crdownload or .zip/.rar file found yet. Waiting...")
            time.sleep(check_interval)

    if not temp_files:
        print("[Warning] No .crdownload file detected within 5 minutes.")
        return False

    print(f"Monitoring {download_folder} for file stabilization and conversion to .zip/.rar...")

    # Step 2: Monitor file stability & conversion
    while time.time() - start_time < timeout:
        files = os.listdir(download_folder)

        if not files:
            log_and_print("[Step] No files detected. Waiting...")
            log_and_print("........................................")
            time.sleep(check_interval)
            continue

        # Check if a .zip or .rar file has been created (download is complete)
        archive_files = [file for file in files if file.endswith(".zip") or file.endswith(".rar")]
        if archive_files:
            print(f"[Step] Archive files detected: {archive_files}. Download considered complete!")
            return True

        # Get file sizes (only monitor the active download files)
        active_files = [file for file in files if file.endswith(".crdownload")]
        current_sizes = {file: os.path.getsize(os.path.join(download_folder, file)) for file in active_files}
        print(f"[Step] Current file sizes: {current_sizes}")

        # Check if file sizes are stable
        if last_sizes and last_sizes == current_sizes:
            stable_count += 1
            print(f"[Step] File sizes unchanged for {stable_count}/{stability_checks} checks.")
        else:
            stable_count = 0  # Reset if size changes
            print("[Step] File sizes changed. Resetting stability counter.")

        # If file sizes have been stable for the required checks, continue monitoring for conversion
        if stable_count >= stability_checks:
            print("[Step] File size stable. Waiting for conversion to .zip or .rar...")

        last_sizes = current_sizes
        time.sleep(check_interval)

    log_and_print("[Warning] Download did not complete within the timeout period.")
    return False

# Move the file after Complete
def move_downloaded_file(download_folder, target_folder):
    if wait_for_download_completion(download_folder):
        files = os.listdir(download_folder)
        files.sort(key=lambda x: os.path.getctime(os.path.join(download_folder, x)), reverse=True)

        if files:
            latest_file = os.path.join(download_folder, files[0])  # Get the latest file
            shutil.move(latest_file, target_folder)

            file_extension = os.path.splitext(latest_file)[1]  # Extract the original file extension
            target_file_path = os.path.join(target_folder, files[0])  # Original name in target folder
            renamed_file_path = os.path.join(target_folder, f"document{file_extension}")  # Renamed file path
            extraction_path = os.path.join(target_folder, "Documents")
            os.rename(target_file_path, renamed_file_path)  # Rename in the target folder
            log_and_print(f"Moved file to {target_folder}")
            log_and_print("........................................")

            # Check if the file is a zip or rar archive
            if file_extension.lower() == ".zip":
                with zipfile.ZipFile(renamed_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extraction_path)
                os.remove(renamed_file_path)  # Delete the original zip file
                log_and_print(f"Extracted and deleted {renamed_file_path}")
                log_and_print("........................................")

            elif file_extension.lower() == ".rar":
                extracted_folder = os.path.join(target_folder, "extracted")
                os.makedirs(extracted_folder, exist_ok=True)
                patoolib.extract_archive(renamed_file_path, outdir=extracted_folder)
                os.remove(renamed_file_path)  # Delete the original rar file
                log_and_print(f"Extracted and deleted {renamed_file_path}")
                log_and_print("........................................")
    else:
        log_and_print("Download did not complete, skipping move operation.")

# Delete any zip Previously located
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

# calculate End Date
def calculate_date_range(start_date, cycle):
    """
    Calculate end date based on user input of 'cycle':
    - 'W': Weekly cycle -> end date = start date + 6 days
    - 'M': Monthly cycle -> end date = last date of the month
    """
    start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")

    if cycle == 'W':
        end_date_obj = start_date_obj + timedelta(days=6)  # Weekly end date is 6 days after start
    elif cycle == 'M':
        end_date_obj = start_date_obj.replace(day=1) + relativedelta(day=31)  # Move to last day of month
    else:
        raise ValueError("Invalid cycle. Use 'W' for weekly or 'M' for monthly.")

    return start_date_obj.strftime("%d/%m/%Y"), end_date_obj.strftime("%d/%m/%Y")

# Calculate Next Periods
def increment_date_range(start_date, end_date, cycle):
    """
    Increment date range based on the cycle:
    - 'W': Increment by 7 days
    - 'M': Increment by 1 month, maintaining end-of-month logic
    """
    start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
    end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")

    if cycle == 'W':
        new_start_date_obj = start_date_obj + timedelta(days=7)
        new_end_date_obj = new_start_date_obj + timedelta(days=6)
    elif cycle == 'M':
        new_start_date_obj = start_date_obj + relativedelta(months=1)
        new_end_date_obj = new_start_date_obj.replace(day=1) + relativedelta(day=31)
    else:
        raise ValueError("Invalid cycle. Use 'W' for weekly or 'M' for monthly.")

    return new_start_date_obj.strftime("%d/%m/%Y"), new_end_date_obj.strftime("%d/%m/%Y")

# Wait for an element to appear on page
def wait_for_element(driver, xpath, timeout=10):
    """Waits for an element to be present on the page before returning it."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

# Retry if not done
#def retry_with_backoff(wait_for_element, driver, xpath, timeout=50):
   # return WebDriverWait(driver, timeout).until(
     #   EC.presence_of_element_located((By.XPATH, xpath))
   # )

def retry_with_backoff(func, *args, max_attempts=5, initial_wait=1, wait_factor=2, **kwargs):
    """Retries a function with exponential backoff in case of exceptions."""
    wait_time = initial_wait
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(wait_time)
            wait_time *= wait_factor  # Increase wait time exponentially

# Function to validate date input
def get_valid_date(prompt):
    while True:
        date_str = input(prompt)
        try:
            valid_date = datetime.strptime(date_str, "%d/%m/%Y")  # Validate format
            return date_str  # Return valid date string
        except ValueError:
            print("Invalid date format. Please enter in dd/mm/yyyy format.")

# Function to validate numeric input
def get_valid_integer(prompt):
    while True:
        num_str = input(prompt)
        if num_str.isdigit():
            return int(num_str)
        else:
            print("Invalid input. Please enter a valid number.")
            
#ALL Functions###########################################################################################################################################################




#Xpath or URL or Classes###########################################################################################################################################################

URL = "https://planning.baberghmidsuffolk.gov.uk/online-applications/search.do?action=advanced"
Xpath_start_date = "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[1]/input"
Xpath_end_date = "/html/body/div/div/div[3]/div[3]/div[2]/form/div[3]/fieldset/div[4]/div[2]/input"
Xpath_Search = "/html/body/div/div/div[3]/div[3]/div[2]/form/div[4]/input[2]"
dropdownID = "resultsPerPage" ###per page set to 100
SetPageGO = "/html/body/div/div/div[3]/div[3]/div[2]/form/input[4]"
SearchresultsClass = "summaryLinkTextClamp"
SubFolder_Name = "/html/body/div/div/div[3]/div[3]/div[9]/table/tbody/tr[1]/td"
Back_Page = "/html/body/div/div/div[3]/div[3]/div[2]/ul/li[1]/a"

Summary = "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[1]/a"
Further_Info = "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[2]/a"
Contacts = "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[3]/a"
Imp_Dates = "/html/body/div/div/div[3]/div[3]/ul/li[1]/ul/li[4]/a"
Comments = "/html/body/div/div/div[3]/div[3]/ul/li[2]/a"
Pub_Comments = "/html/body/div/div/div[3]/div[3]/ul/li[2]/ul/li[2]/a"
Con_Comments = "/html/body/div/div/div[3]/div[3]/ul/li[2]/ul/li[3]/a"
Rel_Cases = "/html/body/div/div/div[3]/div[3]/ul/li[5]/a"
Constra = "/html/body/div/div/div[3]/div[3]/ul/li[3]/a"

Docs_Count = "/html/body/div/div/div[3]/div[3]/ul/li[4]/span"
Docs_Count_2 = "/html/body/div/div/div[3]/div[3]/ul/li[4]/a/span"
Documents_download = "/html/body/div/div/div[3]/div[3]/ul/li[4]/a"
table_id = "Documents"  # Table ID containing checkboxes
check_boxes_Class = "bulkCheck"
Download_Files = "/html/body/div/div/div[3]/div[3]/div[9]/form/button"

MaxDownload = 49


#Xpath or URL or Classes###########################################################################################################################################################

#Inputs###########################################################################################################################################################
# User inputs
# Get the filename on Cmd
filename = os.path.basename(__file__)
print(f"Script running from: {filename}")



start_date = get_valid_date("Enter start date (dd/mm/yyyy): ")

cycle = input("Enter download cycle (W for Weekly, M for Monthly) [Default: M]: ").strip().upper()
if cycle == "":
    cycle = "M"  # Set default to Monthly
elif cycle not in ["W", "M"]:
    print("Invalid input. Defaulting to Monthly (M).")
    cycle = "M"

if cycle == "M":
    Period_Cycle = "Monthly"
elif cycle not in ["M"]:
    Period_Cycle = "Weekly"

count_label = "weeks" if cycle == "W" else "months"
#count = get_valid_integer(f"Enter the number of {count_label} to end the loop: ")
count = 780
# Ensure end_date is calculated before incrementing
start_date, end_date = calculate_date_range(start_date, cycle)  

try:
    # Calculate initial range
    initial_start, initial_end = calculate_date_range(start_date, cycle)
    
    # Calculate next range
    next_start, next_end = increment_date_range(initial_start, initial_end, cycle)

    # Output results
    log_and_print(f"Website: {URL}") 
    log_and_print(f"Initial Range: {initial_start} to {initial_end}")
    log_and_print(f"Cycle = {Period_Cycle}")
    log_and_print(f"Next Range: {next_start} to {next_end}")
    log_and_print(f"Month_count = {count}")
    i = 1
    exit_loops = False
except ValueError as e:
    print(f"Error: {e}")

#Inputs###########################################################################################################################################################




#Loop Starts###########################################################################################################################################################

# Loop while count is less than or equal to 5
while count <= 1000: 

    # Initialize WebDriver options
    formatted_download_path = f"{start_date.replace('/', '')} to {end_date.replace('/', '')}"
    download_path = os.path.abspath(formatted_download_path)
    if os.path.exists(download_path) and os.path.isdir(download_path):
        subfolder_count = sum(os.path.isdir(os.path.join(download_path, item)) for item in os.listdir(download_path))
        print(f"Downloads exists. Number of Download Results exists: {subfolder_count}")
        start_result = subfolder_count
        start_page = int(math.ceil(start_result / 100))
        start_result = int(start_result - (start_page - 1) * 100)
        i = start_result
        log_and_print(f"start_page Change to = {start_page}")
        log_and_print(f"start_result Change to = {start_result}")
        
    
    else:
        print("Folder does not exist Creating it.")   
        os.makedirs(download_path)
        #start_page = int(input("Enter the page number to start from: "))
        start_result = get_valid_integer("Enter the result number to start from: ")
        start_page = int(math.ceil(start_result / 100))
        start_result = int(start_result - (start_page - 1) * 100)
        i = start_result
        log_and_print(f"start_page = {start_page}")
        log_and_print(f"start_result = {start_result}")

    options = webdriver.EdgeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    })

    driver = webdriver.Edge(options=options)
    if __name__ == "__main__":
        driver.get(URL)###URL
        #driver.minimize_window()  # Hides the browser window
    else:
        log_and_print("Browser Crushed")

    #Select a random user agent from the list and add it to the options
    selected_user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={selected_user_agent}')

    driver.get(URL)###URL
    log_and_print(URL)###URL
    time.sleep(random.uniform(0.5, 1.5))

    log_and_print("Inputing Dates and Search")
    
    # Input date range
    retry_with_backoff(wait_for_element, driver, Xpath_start_date).send_keys(start_date)###Start Date
    retry_with_backoff(wait_for_element, driver, Xpath_end_date).send_keys(end_date)###End Date
    retry_with_backoff(wait_for_element, driver, Xpath_Search).click()###Search

    time.sleep(random.uniform(2, 5))
    log_and_print("Arrenging Page for extraction 100 Results per Page")
    # Set results per page
    dropdown = driver.find_element(By.ID, dropdownID)###per page set to 100
    move_mouse_and_scroll(driver, dropdown)
    dropdown.send_keys("100")
    retry_with_backoff(wait_for_element, driver, SetPageGO).click()###per page set to 100

    time.sleep(random.uniform(0.5, 1.5))
    # Find elements with the class name "summaryLinkTextClamp"
    elements = driver.find_elements(By.CLASS_NAME, SearchresultsClass)
    countSearch = len(elements)
    # Print the count
    print(f"Number of results in current Page: {len(elements)}")

    # Initialize page number before loop starts
    page_number = start_page
   
    log_and_print(f"start_page = {page_number}")
    
    while True:
        log_and_print("=============================================================================================================")
        log_and_print(f"Processing page {page_number}...")
        log_and_print("=============================================================================================================")
        if not is_driver_alive(driver):
            log_and_print(f"Error: Browser is closed. Stopping execution.")
            break  # Exit the loop if browser is closed

        
        try:
            if page_number > 1:
                for _ in range(page_number - 1):
                    next_page_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
                    )
                    move_mouse_and_scroll(driver, next_page_button)
                    next_page_button.click()
                    log_and_print("===================================================================================================================")
                    time.sleep(random.uniform(0.5, 1.5))
                    # Find elements with the class name "summaryLinkTextClamp"
                    elements = driver.find_elements(By.CLASS_NAME, SearchresultsClass)
                    countSearch = len(elements)
                    # Print the count
                    print(f"Number of results in current Page: {len(elements)}")
                    
        except Exception:
            log_and_print("Reached last available page or invalid start page.")
            break


        
        while i <= countSearch:
                if not is_driver_alive(driver):
                    log_and_print(f"Error: Browser is closed. Stopping execution.")
                    break  # Exit the loop if browser is closed

                try:
                    if not is_driver_alive(driver):
                        log_and_print(f"Error: Browser is closed. Stopping execution.")
                        break  # Exit the loop if browser is closed
                    
                    log_and_print("-------------------------------------------------------------------------------------------------------------")
                    log_and_print(f"Processing Result {i} out of {countSearch} of Page {page_number}")
                    log_and_print("-------------------------------------------------------------------------------------------------------------")

                    result_xpath = f"/html/body/div/div/div[3]/div[3]/div[3]/div[1]/ul/li[{i}]/a"                     ################ Result ########################
                    
                    #move_mouse_and_scroll(driver, result_xpath)
                    result_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, result_xpath))
                    )
                    result_element.click()
                    
                    element = retry_with_backoff(wait_for_element, driver, SubFolder_Name, 10)### Name for Subfolder
                    result_name = ''.join(c for c in element.text if c.isalnum() or c in (' ', '_', '-')).strip()

                    time.sleep(random.uniform(0.5, 1.5))
                    subFolderPath = os.path.join(download_path, result_name)
                    if not os.path.exists(subFolderPath):
                        os.makedirs(subFolderPath)

                    extract_and_save(driver, Summary, subFolderPath, "Summary.txt")###
                    extract_and_save(driver, Further_Info, subFolderPath, "Further Information.txt")###
                    extract_and_save(driver, Contacts, subFolderPath, "Contacts.txt")###
                    extract_and_save(driver, Imp_Dates, subFolderPath, "Important Dates.txt")###
                    extract_and_save(driver, Comments, subFolderPath, "Comments.txt")###
                    extract_and_save(driver, Pub_Comments, subFolderPath, "Pub_Comments.txt")###
                    extract_and_save(driver, Con_Comments, subFolderPath, "Con_Comments.txt")###
                    extract_and_save(driver, Rel_Cases, subFolderPath, "Related Cases.txt")###
                    extract_and_save(driver, Constra, subFolderPath, "Constraints.txt")###

                    try:
                        span_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, Docs_Count))
                        )
                        span_text = span_element.text.strip().replace("\n", " ").replace("\t", " ")
                        # Use regex to extract the number inside parentheses
                        match = re.search(r"\(\s*(\d+)\s*\)", span_text)  # Handles spaces inside parentheses
                        document_count = int(match.group(1) if match else "0")
                        print(f"Downloadable contents: {document_count}")
                    except:
                        span_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, Docs_Count_2)) #
                        )
                        move_mouse_and_scroll(driver, span_element)
                        span_text = span_element.text.strip().replace("\n", " ").replace("\t", " ")
                        # Use regex to extract the number inside parentheses
                        match = re.search(r"\(\s*(\d+)\s*\)", span_text)  # Handles spaces inside parentheses
                        document_count = int(match.group(1) if match else "0")
                        print(f"Downloadable contents : {document_count}")

                    if document_count == 0:
                            log_and_print(f"No Downloadable content:")
                            retry_with_backoff(wait_for_element, driver, Back_Page).click()### Back to Page
                            time.sleep(random.uniform(0.5, 1.5))
                    else:
                        # Handle Document Download
                        download_button = retry_with_backoff(wait_for_element, driver, Documents_download, 50)### Document
                        move_mouse_and_scroll(driver, download_button)
                        download_button.click()
                        time.sleep(random.uniform(0.5, 1.5))

                        checkcountStart = 1
                        checkcountEnd = document_count
                        
                        

                        # **Find the table**
                        try:
                            table = driver.find_element(By.ID, table_id)
                            rows = table.find_elements(By.TAG_NAME, "tr")  # Get all rows
                            total_documents = len(rows) - 1  # Subtract 1 to remove the header row
                            print(f"Total documents found: {total_documents}")
                        except Exception as e:
                            print(f"Error locating table: {e}")
                        
                        if math.ceil(document_count / MaxDownload) > 0:
                            download_counting = math.ceil(document_count / MaxDownload)

                            log_and_print(f"Documents count {download_counting}")

                            
                            for batch in range(download_counting):
                                try:
                                    # **Step 1: Uncheck all checkboxes before selecting new ones**
                                    checkboxes = table.find_elements(By.CLASS_NAME, check_boxes_Class)
                                    for checkbox in checkboxes:
                                        if checkbox.is_selected():
                                            checkbox.click()
                                            time.sleep(0.1)  # Small delay for stability
                                    print("All checkboxes are now unchecked.")

                                except Exception as e:
                                    print(f"Error unchecking checkboxes: {e}")

                                # **Step 2: Select the next batch of checkboxes**
                                checkcountStart = batch * MaxDownload + 1  # Adjust starting row index
                                checkcountEnd = min(checkcountStart + MaxDownload, total_documents + 1)  # Ensure within row count

                                for row in rows[checkcountStart:checkcountEnd]:
                                    try:
                                        checkbox = row.find_element(By.CLASS_NAME, check_boxes_Class)  # Find checkbox inside row

                                        # **Scroll into view using JavaScript**
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                        time.sleep(0.1)  # Allow time for scrolling

                                        # **Click using ActionChains to avoid interception**
                                        ActionChains(driver).move_to_element(checkbox).click().perform()
                                        time.sleep(0.1)  # Small delay to avoid potential issues

                                        print(f"Checked checkbox in row {rows.index(row)}")

                                    except Exception as e:
                                        print(f"Error clicking checkbox in row {rows.index(row)}: {e}")

                                # **Step 3: Click Download Button**
                                try:
                                    delete_zip_and_rar_files(download_path)
                                    download_link = retry_with_backoff(wait_for_element, driver, Download_Files, 10)### Download Link
                                    move_mouse_and_scroll(driver, download_link)
                                    download_link.click()
                                    time.sleep(random.uniform(10, 15))
                                    move_downloaded_file(download_path, subFolderPath)
                                    log_and_print("Download completed.")
                                    log_and_print("........................................")

                                except Exception as e:
                                    print(f"Error clicking download button: {e}")

                                print("All batches completed successfully.")
                                log_and_print("........................................")

                                    ###################
                                
                                log_and_print(f"Scraping range {start_date} to {end_date}")
                                    # Update checkcount range for the next batch
                                checkcountStart += MaxDownload
                                checkcountEnd += MaxDownload
                                
                            
                        
                        #driver.close()
                        #driver.switch_to.window(driver.window_handles[0])

                        retry_with_backoff(wait_for_element, driver, Back_Page).click()### Back to Page
                        time.sleep(random.uniform(0.5, 1.5))

                            #####################################################################################
                    
                    i += 1
                    print(i)
                    if i > countSearch:
                        try:
                            page_number += 1
                            next_page_button = driver.find_element(By.LINK_TEXT, "Next")### Next Page
                            move_mouse_and_scroll(driver, next_page_button)
                            next_page_button.click()
                            log_and_print("========================================================================================================================")
                            

                                # Find elements with the class name "summaryLinkTextClamp"
                            elements = driver.find_elements(By.CLASS_NAME, SearchresultsClass)
                            countSearch = len(elements)
                            # Print the count
                            print(f"Number of results in current page: {len(elements)}")
        
                            
                            i = 1
                            start_result = 1  # Restart loop from 1 on the new page
                            time.sleep(random.uniform(0.5, 1.5))
                        except Exception:
                            log_and_print("No more pages available.")
                            driver.quit()
                            start_date, end_date = increment_date_range(start_date, end_date, cycle)
                            log_and_print(f"Scraping range {start_date} to {end_date}")
                            i = 1
                            start_result = 1
                            start_page = 1
                            print(i)
                            break  # Break inner loop
                except Exception:
                    log_and_print("This Period Completed.")
                    break  # Break inner loop

        
                  
            
    
    
log_and_print("Data extraction completed.")
