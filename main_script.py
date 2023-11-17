import asyncio
import time
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
from pdf_scraper.scraper import scrape_website
from pdf_scraper.utils import read_websites_from_file, read_config_from_file
from pdf_scraper.database import save_to_sql_server

def wrapper(task):
    return asyncio.run(task)

def main():
    print("Start", time.ctime())

    # Load configuration from the file
    config = read_config_from_file('pdf_scraper/config.json')

    # List of websites to scrape
    websites = read_websites_from_file(config["websites_file"])

    # Set the maximum number of threads to use
    max_threads = config["max_threads"]

    # Specify the folder to save the PDF files
    download_folder = 'pdf_files'

    # Create the download folder if it doesn't exist
    os.makedirs(download_folder, exist_ok=True)

    # Create a ThreadPoolExecutor with the specified maximum number of threads
    with ThreadPoolExecutor(max_threads) as executor:
        tasks = [scrape_website(website, download_folder) for website in websites]
        results = executor.map(wrapper, tasks)

    # Flatten the list of lists into a single list of dictionaries
    pdf_metadata_list = [item for sublist in results for item in sublist]

    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(pdf_metadata_list)

    # Save the DataFrame to an Excel file
    df.to_excel('pdf_metadata.xlsx', index=False)    

    save_to_sql_server(pdf_metadata_list)  

if __name__ == "__main__":
    main()