from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.process_manager import ProcessManager

from datetime import time
import multiprocessing
from lib.scanner import Scanner
from lib.product import Product


class Crawler(object):
    def __init__(self, args, pm:ProcessManager):
        self.args = args
        self.pm = pm
        self.num_pages = self.get_num_pages(args.max_pages)

    def get_num_pages(self, max_pages: int):
        scanner = Scanner()
        num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
        scanner.accept_cookies()
        return min(num_pages, max_pages)  

    def get_scanner(self, scanner, count) -> Scanner:
        if count % 50 == 0: 
            scanner.close
            scanner = Scanner()
            time.sleep(5.0)
        return scanner

    def crawl(self, q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue, q_stop: multiprocessing.Queue):
        scanner = Scanner()
        count = 0
        while(True):
            incoming = q_incoming.get()
            if type(incoming) is int:
                print(f"incoming crawl: {incoming}")
                count += 1
                scanner = self.get_scanner(count, scanner)

                index = incoming            
                page_uri = f"https://www.usedproducts.nl/page/{index}/?s&post_type=product&vestiging=0"
                # print(f"Loading summary page {incoming}")
                try:
                    for product in scanner.scan(page_uri):
                        if self.pm.already_stored(product):
                            self.pm.update_product_in_db(product)
                        else:
                            q_outgoing.put(product)
                except Exception as e:
                    print(f"### Error: Failed loading summary page {index}: {page_uri} with error {str(e)}")
                    scanner = Scanner()
                if index == self.num_pages - 1:
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
                if count % 50 == 0: 
                    self.get_scanner(count, scanner)
                product = incoming
                # print(f"Loading product: {product.name}")
                try:
                    scanner.add_details(product)
                    product.fill_derived(including_dates=True)
                    q_outgoing.put(product)
                except Exception as e:
                    scanner = Scanner()
                    print(f"### Error: Failed loading product {product.link} with error {str(e)}")
            if type(incoming) is str:
                print("Exiting details crawler process")
                return
