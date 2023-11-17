import requests
import os
import json
async def get_pdf_metadata(link, download_folder):
    try:
        # Fetch PDF file size using the requests library
        response = requests.head(link)
        file_size = int(response.headers.get('Content-Length', 0))

        # Download the PDF file
        pdf_file_path = os.path.join(download_folder, f"{hash(link)}.pdf")
        with open(pdf_file_path, 'wb') as pdf_file:
            response = requests.get(link)
            pdf_file.write(response.content)

        return {'url': link, 'title': '', 'file_size': file_size, 'file_path': pdf_file_path}

    except Exception as e:
        print(f"Error while fetching metadata for {link}: {e}")
        return {'url': link, 'title': '', 'file_size': None, 'file_path': None}
    
async def get_title(page, link):
    try:
        # Extract the title of the PDF link using pyppeteer
        title = await page.evaluate('''(link) => {
            const pdfLink = document.querySelector(`a[href="${link}"]`);
            return pdfLink ? pdfLink.innerText.trim() : '';
        }''', link)

        return title

    except Exception as e:
        print(f"Error while fetching title for {link}: {e}")
        return ''

def read_websites_from_file(file_path):
    with open(file_path, 'r') as file:        
        websites = [line.strip() for line in file.readlines()]
    return websites

def read_config_from_file(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config