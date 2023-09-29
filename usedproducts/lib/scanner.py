import math
import re

from bs4 import BeautifulSoup
from lib.product import Product
from lib.products import Products

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.common.by import By
# from bs4 import Tag, ResultSet


class PageLoaded(object):
    def __call__(self, driver):
        r = driver.execute_script("return document.readyState")
        return r == "complete"
    
class Scanner(object):

    def __init__(self):
        # options = selenium.webdriver.ChromeOptions()
        # options.set_capability('acceptInsecureCerts', True)
        # options.add_argument('--disable-notifications')

        # options.add_argument('--auth-server-whitelist=*')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--headless')
        self.products = Products()
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.set_capability('acceptInsecureCerts', True)
        options.add_argument('--disable-notifications')

        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.set_page_load_timeout(15)

    def __del__(self):
        if hasattr(self, 'browser') and self.browser is not None:
            self.browser.quit()

    def close(self):
        if hasattr(self, 'browser') and self.browser is not None:
            self.browser.quit()

    def get_num_pages(self, uri):
        self.browser.get(uri)
        wait = WebDriverWait(self.browser, 10)
        wait.until(PageLoaded())
        content = self.browser.page_source
        soup = BeautifulSoup(content, "html.parser")

        text = soup.find(class_="woocommerce-result-count").text
        # text is expected to be in the form: "        1–12 van de 28125 producten"
        matches = re.findall('\d+', text)
        num_pages = math.ceil(int(matches[2]) / int(matches[1]))
        return num_pages
    
    def accept_cookies(self):
        self.browser.find_element(By.ID, "allowcookie").click()
    
    def scan(self, uri):
        self.browser.get(uri)
        wait = WebDriverWait(self.browser, 10)
        wait.until(PageLoaded())
        content = self.browser.page_source
        soup = BeautifulSoup(content, "html.parser")
        
        product_sections = soup.find_all(class_="product-thumnail")
        for section in product_sections:
            
            anchor = section.find(class_="product-name-collection").a
            description = anchor.text
            link = anchor.get('href')
            price = section.find(class_="product-price").div.span.text
            p = Product(description, link, price)
            self.products.append(p)