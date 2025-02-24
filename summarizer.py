import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

# Get the OpenAI API key from the environment variables (set in .env)
key = os.getenv('OPENAI_API_KEY')

if key is None:
    raise ValueError("API key is missing. Please set OPENAI_API_KEY in the environment or .env file.")

# Initialize OpenAI with the API key
openai = OpenAI(api_key=key)

class Website:
    def __init__(self, url, use_selenium=False):
        self.url = url

        if use_selenium:
            self.text, self.title = self.scrape_with_selenium(url)
        else:
            self.text, self.title = self.scrape_with_requests(url)

    def scrape_with_requests(self, url):
        """Scrapes webpage using requests (for non-JS heavy sites)."""
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        
        # Remove unnecessary elements
        for tag in soup(["script", "style", "img", "input"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text, title

    def scrape_with_selenium(self, url):
        """Scrapes webpage using Selenium (for JS-heavy sites)."""
        
        # Set Chrome options
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Automatically install and manage ChromeDriver
        service = Service(ChromeDriverManager().install())

        # Start Chrome WebDriver
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # Get page source after JavaScript execution
        page_source = driver.page_source
        driver.quit()

        # Parse content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        
        for tag in soup(["script", "style", "img", "input"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text, title

def summarize_text(text, title):
    """Generate summary using OpenAI API"""
    messages = [
        {"role": "system", "content": "You are a summarizer. Provide a concise summary of the given website content."},
        {"role": "user", "content": f"Title: {title}\n\nContent: {text}\n\nSummarize this."}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # switch this model if needed
        messages=messages
    )
    return response.choices[0].message.content
