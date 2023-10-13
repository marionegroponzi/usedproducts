
import time
import multiprocessing
from lib.scanner import Scanner
from lib.product import Product
from lib.db_manager import DBManager


class Crawler(object):

    def __init__(self):
        pass

    def get_num_pages(max_pages: int):
        scanner = Scanner()
        num = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
        scanner.accept_cookies()
        return min(num, max_pages)  

    def get_scanner(self, scanner:Scanner, count:int) -> Scanner:
        if count % 50 == 0: 
            scanner.close
            scanner = Scanner()
            time.sleep(5.0)
        return scanner

    def crawl(self, q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue, q_stop: multiprocessing.Queue, num_pages:int):
        scanner = Scanner()
        db_manager = DBManager()
        count = 0
        while(True):
            incoming = q_incoming.get()
            if type(incoming) is int:
                print(f"incoming crawl: {incoming} with num_pages {num_pages}")
                count += 1
                scanner = self.get_scanner(scanner, count)

                index = incoming            
                page_uri = f"https://www.usedproducts.nl/page/{index}/?s&post_type=product&vestiging=0"
                # print(f"Loading summary page {incoming}")
                try:
                    for product in scanner.scan(page_uri):
                        if db_manager.already_stored(product):
                            db_manager.update_product_in_db(product)
                        else:
                            q_outgoing.put(product)
                except Exception as e:
                    print(f"### Error: Failed loading summary page {index}: {page_uri} with error {str(e)}")
                    scanner = Scanner()
                if index == num_pages - 1:
                    print("Putting an end to this suffering")
                    q_stop.put("Finish")
            if type(incoming) is str:
                print("Exiting page crawler process")
                return
            
    def crawl_details(self, q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue):
        scanner = Scanner()
        count = 0
        while(True):
            incoming = q_incoming.get()
            if type(incoming) is Product:
                print(f"incoming details: {incoming.name}")
                count += 1
                scanner = self.get_scanner(scanner, count)
                product = incoming
                # print(f"Loading product: {product.name}")
                try:
                    scanner.add_details(product)
                    product.fill_derived(including_dates=True)
                    q_outgoing.put(product)
                except Exception as e:
                    scanner = Scanner()
                    print(f"### Error: Failed loading product {product.link}") # with error {str(e)}
            if type(incoming) is str:
                print("Exiting details crawler process")
                return
