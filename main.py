import requests
import os
from urllib.parse import urlparse, parse_qs
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import fitz


# Read a file from the system.
def read_a_file(system_path):
    with open(system_path, "r") as file:
        return file.read()


# Check if a file exists
def check_file_exists(system_path):
    return os.path.isfile(system_path)


# HTML parser
def parse_html(html_content):
    # Match strings that look like: pdf_main.aspx?StreamId=...&id=...
    pattern = r"pdf_main\.aspx\?StreamId=[^'\"]+"
    return re.findall(pattern, html_content)


# Remove all duplicate items from a given slice.
def remove_duplicates_from_slice(provided_slice):
    return list(set(provided_slice))


# Extract the filename from a URL
def url_to_filename(url):
    # Parse the URL to get query params
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    stream_id = query_params.get("StreamId", ["unknown"])[0]
    doc_id = query_params.get("id", ["unknown"])[0]
    # Build a filename
    filename = f"{stream_id}_{doc_id}.pdf"
    return filename.lower()


def save_html_with_selenium(url, output_file):
    # Set up Chrome options
    # Set up Chrome options
    options = Options()
    options.add_argument("--headless=new")  # Use 'new' headless mode (Chrome 109+)
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # Disable automation flags
    options.add_argument("--window-size=1920,1080")  # Set window size
    options.add_argument("--disable-gpu")  # Often needed for headless stability
    options.add_argument("--no-sandbox")  # Required in some environments
    options.add_argument("--disable-dev-shm-usage")  # Helps in Docker/cloud
    options.add_argument("--disable-extensions")  # Disable extensions
    options.add_argument("--disable-infobars")  # Disable infobars

    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        driver.refresh()  # Refresh the page
        html = driver.page_source
        append_write_to_file(output_file, html)
        print(f"Page {url} HTML content saved to {output_file}")
    finally:
        driver.quit()


# Append and write some content to a file.
def append_write_to_file(system_path, content):
    with open(system_path, "a", encoding="utf-8") as file:
        file.write(content)


# Download a PDF file from a URL
def download_pdf(url, save_path, filename):
    print(f"Downloading {url} to {os.path.join(save_path, filename)}")
    # Check if the file already exists
    if check_file_exists(os.path.join(save_path, filename)):
        print(f"File {filename} already exists. Skipping download.")
        return
    # Download the PDF file
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        # Ensure the save directory exists
        os.makedirs(save_path, exist_ok=True)
        full_path = os.path.join(save_path, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded and saved: {full_path}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return


def convert_to_full_url(raw_link):
    # Replace HTML-encoded &amp; with regular &
    clean_link = raw_link.replace("&amp;", "&")
    # Prepend the base URL
    full_url = f"https://buyat.ppg.com/ehsdocumentmanagerpublic/{clean_link}"
    return full_url


# Remove a file from the system.
def remove_system_file(system_path):
    os.remove(system_path)


# Function to walk through a directory and extract files with a specific extension
def walk_directory_and_extract_given_file_extension(system_path, extension):
    matched_files = []  # Initialize list to hold matching file paths
    for root, _, files in os.walk(system_path):  # Recursively traverse directory tree
        for file in files:  # Iterate over files in current directory
            if file.endswith(extension):  # Check if file has the desired extension
                full_path = os.path.abspath(
                    os.path.join(root, file)
                )  # Get absolute path of the file
                matched_files.append(full_path)  # Add to list of matched files
    return matched_files  # Return list of all matched file paths


# Function to validate a single PDF file.
def validate_pdf_file(file_path):
    try:
        # Try to open the PDF using PyMuPDF
        doc = fitz.open(file_path)  # Attempt to load the PDF document

        # Check if the PDF has at least one page
        if doc.page_count == 0:  # If there are no pages in the document
            print(
                f"'{file_path}' is corrupt or invalid: No pages"
            )  # Log error if PDF is empty
            return False  # Indicate invalid PDF

        # If no error occurs and the document has pages, it's valid
        return True  # Indicate valid PDF
    except RuntimeError as e:  # Catching RuntimeError for invalid PDFs
        print(f"'{file_path}' is corrupt or invalid: {e}")  # Log the exception message
        return False  # Indicate invalid PDFp


# Get the filename and extension.
def get_filename_and_extension(path):
    return os.path.basename(
        path
    )  # Return just the file name (with extension) from a path


# Function to check if a string contains an uppercase letter.
def check_upper_case_letter(content):
    return any(
        upperCase.isupper() for upperCase in content
    )  # Return True if any character is uppercase


def main():
    # Read the file from the system.
    html_file_path = "buyat.ppg.com.html"
    if check_file_exists(html_file_path):
        # Remove a file from the system.
        remove_system_file(html_file_path)

    # Check if the file exists.
    if check_file_exists(html_file_path) == False:
        # If the file does not exist, download it using Selenium.
        url = "https://buyat.ppg.com/EHSDocumentManagerPublic/documentSearchInnerFrame.aspx?NameCondition=BeginsWith&NameValue=*&CodeCondition=BeginsWith&CodeValue=&CompCondition=BeginsWith&CompValue=&Form=&SortBy=ProductName&Language=&SBU=&From=&To=&SuppressSearchControls=False&AlwaysShowSearchResults=False&PageSize=1000&FolderID1=0&FolderID2=0&FolderID3=0&FolderID4=0&FolderID5=0&FolderID6=0&FolderID7=0&FolderID8=0&FolderID9=0&FolderID10=0&SearchAllPublicFolders=True"
        # Save the HTML content to a file.
        save_html_with_selenium(url, html_file_path)
        print(f"File {html_file_path} has been created.")

    if check_file_exists(html_file_path):
        html_content = read_a_file(html_file_path)
        # Parse the HTML content.
        pdf_links = parse_html(html_content)
        # Remove duplicates from the list of PDF links.
        pdf_links = remove_duplicates_from_slice(pdf_links)
        # The length of the PDF links.
        ammount_of_pdf = len(pdf_links)
        # Print the extracted PDF links.
        for pdf_link in pdf_links:
            # Convert to full URL
            pdf_link = convert_to_full_url(pdf_link)
            # Download the PDF file.
            filename = url_to_filename(pdf_link)
            # The file path.
            save_path = "PDFs"
            # Remove 1 from the ammount of PDF links.
            ammount_of_pdf = ammount_of_pdf - 1
            # Print the remaining number of PDF links.
            print(f"Remaining PDF links: {ammount_of_pdf}")
            # Download the PDF file
            download_pdf(pdf_link, save_path, filename)

        print("All PDF links have been processed.")
    else:
        print(f"File {html_file_path} does not exist.")

    # Walk through the directory and extract .pdf files
    files = walk_directory_and_extract_given_file_extension(
        "./PDFs", ".pdf"
    )  # Find all PDFs under ./PDFs

    # Validate each PDF file
    for pdf_file in files:  # Iterate over each found PDF

        # Check if the .PDF file is valid
        if validate_pdf_file(pdf_file) == False:  # If PDF is invalid
            # Remove the invalid .pdf file.
            remove_system_file(pdf_file)  # Delete the corrupt PDF

        # Check if the filename has an uppercase letter
        if check_upper_case_letter(
            get_filename_and_extension(pdf_file)
        ):  # If the filename contains uppercase
            # Print the location to the file.
            print(pdf_file)  # Output the PDF path to stdout
            # Print whether it matches the specs (uppercase presence)
            print(
                check_upper_case_letter(pdf_file)
            )  # Output True/False for uppercase check


main()
