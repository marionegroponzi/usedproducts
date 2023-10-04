#!/usr/bin/env python
import argparse
import json
import os
import urllib3
import logging
import sys

from lib.scanner import Scanner
from lib.products import ProductsContainer
# enable only after pip install -U memory_profiler
# from memory_profiler import profile

def crawl(max_pages):
    scanner = Scanner()
    num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    scanner.accept_cookies()
    for i in range(1,min(num_pages, max_pages)+1):
        page_uri = f"https://www.usedproducts.nl/page/{i}/?s&post_type=product&vestiging=0"
        print(f"Loading summary page {i}: {page_uri}")
        scanner.scan(page_uri)
    scanner.close()
    return scanner.products_container

def crawl_details(products):
    for index, product in enumerate(products):
        print(f"Loading product page {index}: {product.link}")
        if index % 25 == 0:
            # reset the scanner every 25 products to keep the browser "fresh"
            scanner = Scanner()
        product.details = scanner.scan_details(product.link)

    scanner.close()

def load(filename) -> ProductsContainer:
    content = open(filename, "r").read()
    d = json.loads(content)
    return ProductsContainer(d)

# @profile
def main():
    (success, args) = parse_args()
    if not success:
        print("Something wrong with the arguments")
        return
    config_env()

    # if load we assume one wants to refresh all derived data
    # else we assume one wants to store them
    if args.refresh:
        products_container = load(args.load.name)
    else:
        products_container = crawl(args.max_pages)
        crawl_details(products_container.products)

    products_container.fill_derived()
        
    if args.save:
        str_products = products_container.to_json()
        open(args.save.name, "w").write(str_products)
    else:
        print(str_products)

def parse_args():
    parser = argparse.ArgumentParser(
        prog='usedproducts',
        description='Crawler and analyzer for userdproducts.com',
        )
    parser.add_argument('--log', '-l', choices=['DEBUG','INFO','WARN','ERROR'],
                        help='loglevel: DEBUG, INFO, WARN, ERROR (default: ERROR)')
    parser.add_argument('--refresh', '-f', type=argparse.FileType('r'), help='load a json file instead of crawling and update the details for each product')
    parser.add_argument('--save', '-s', type=argparse.FileType('w'), help='save data to a json file')
    parser.add_argument('--max_pages', '-m', type=int, help='maximum number of pages to load', default=sys.maxsize)
    args = parser.parse_args()
    if args.log:
        numeric_level = getattr(logging, args.log.upper())
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.basicConfig(level=numeric_level)
    return (True, args)


def config_env():
    # some pages are self-signed by ABN AMRO, and we don't want to see all the warnings about those
    urllib3.disable_warnings()

    os.environ['PATH'] = f"{os.environ['PATH']}:{os.getcwd()}"


if __name__ == "__main__":
    main()
