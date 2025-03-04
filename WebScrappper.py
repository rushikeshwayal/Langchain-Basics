from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from webdriver_manager.chrome import ChromeDriverManager

class WebScraper:
    def __init__(self, parser_type='bs4', headless=True):
        self.parser_type = parser_type
        self.headless = headless
        self.driver = None
        
        if self.parser_type == 'selenium':
            self._init_selenium_driver()

    def _init_selenium_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def _extract_with_bs4(self, url, elements):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_elements(soup, elements)
        
        except Exception as e:
            print(f"BeautifulSoup extraction error: {str(e)}")
            return None

    def _extract_with_selenium(self, url, elements, wait_for=None, timeout=10):
        try:
            self.driver.get(url)
            
            if wait_for:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return self._parse_elements(soup, elements)
        
        except Exception as e:
            print(f"Selenium extraction error: {str(e)}")
            return None

    def _parse_elements(self, soup, elements):
        result = {}
        for name, selector in elements.items():
            try:
                if selector.get('type') == 'list':
                    items = soup.select(selector['selector'])
                    result[name] = [item.get_text(strip=True) for item in items]
                else:
                    item = soup.select_one(selector['selector'])
                    result[name] = item.get_text(strip=True) if item else None
                
                # Extract attributes if specified
                if selector.get('attribute'):
                    if selector.get('type') == 'list':
                        result[name] = [item[selector['attribute']] for item in items if item.has_attr(selector['attribute'])]
                    else:
                        result[name] = item[selector['attribute']] if item and item.has_attr(selector['attribute']) else None
            except Exception as e:
                print(f"Error parsing element {name}: {str(e)}")
                result[name] = None
        
        return result

    def scrape(self, url, elements_config, wait_for=None):
        """
        Scrape website using configured parser
        :param url: Target URL
        :param elements_config: Dictionary of elements to scrape
        Example config:
        {
            'title': {'selector': 'h1.product-title', 'attribute': 'text'},
            'price': {'selector': 'span.price', 'type': 'list'},
            'images': {'selector': 'img.product-image', 'attribute': 'src', 'type': 'list'}
        }
        :param wait_for: CSS selector to wait for (Selenium only)
        :return: Dictionary with scraped data
        """
        if self.parser_type == 'bs4':
            return self._extract_with_bs4(url, elements_config)
        elif self.parser_type == 'selenium':
            return self._extract_with_selenium(url, elements_config, wait_for)
        else:
            raise ValueError("Invalid parser type. Use 'bs4' or 'selenium'")

    def close(self):
        if self.driver:
            self.driver.quit()



# Configuration for elements to scrape
config = {
    'title': {'selector': 'h1', 'attribute': 'text'},
}

scraper = WebScraper(parser_type='bs4')
result = scraper.scrape(
    url='https://www.blogger.com/blog/post/edit/3785311793894115549/1971625905403679028',
    elements_config=config
)

print(result)