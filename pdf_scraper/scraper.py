from pdf_scraper.utils import get_title, get_pdf_metadata
from pyppeteer import launch

async def scrape_website(url, download_folder):    
    try:        
        browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False
        )
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'domcontentloaded'})
        
        # You can perform scraping operations using page.evaluate or other pyppeteer functions
        title = await page.title()
        print(f"Title of {url}: {title}")

        # Extract PDF links using pyppeteer
        pdf_links = await page.evaluate('''() => {
            const pdfLinks = [];
            for (const link of document.querySelectorAll('a[href$=".pdf"]')) {
                pdfLinks.push(link.href);
            }
            return pdfLinks;
        }''')
        
        # Fetch PDF metadata asynchronously
        pdf_metadata_list = []
        for link in pdf_links:
            title = await get_title(page, link)
            metadata = await get_pdf_metadata(link, download_folder)
            metadata['title'] = title
            pdf_metadata_list.append(metadata)

        await browser.close()

        return pdf_metadata_list     
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return []