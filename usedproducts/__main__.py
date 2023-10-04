#!/usr/bin/env python
import argparse
import json
import os
import urllib3
import logging
import sys
import pymongo

from lib.scanner import Scanner
from lib.product import Product

# enable only after pip install -U memory_profiler
# from memory_profiler import profile

def crawl(num_pages, scanner: Scanner):
    for i in range(1, num_pages + 1):
        page_uri = f"https://www.usedproducts.nl/page/{i}/?s&post_type=product&vestiging=0"
        print(f"Loading summary page {i}: {page_uri}")
        for product in scanner.scan(page_uri):
            yield product

def crawl_details(product: Product, scanner: Scanner):
    print(f"Loading product page: {product.link}")
    product.details = scanner.scan_details(product.link)
    product.fill_derived()
    return product

def save_to_mongo(product, collection):
    if collection is not None:
        # pay attention that inserting the product modifies it. If you need to return it, copy the dict first
        d = product.__dict__
        collection.insert_one(d)

def get_mongo(reset: bool) -> pymongo.collection.Collection:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    coll = client.usedproducts.products
    if reset:
        coll.delete_many({ })
    return coll

def get_num_pages(args, scanner: Scanner):
    num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    scanner.accept_cookies()
    return min(num_pages, args.max_pages)

# @profile
def main():
    (success, args) = parse_args()
    if not success:
        print("Something wrong with the arguments")
        return -1
    config_env()

    coll = get_mongo(args.reset)

    if args.crawl or args.reset:
        main_scanner = Scanner()
        num_pages = get_num_pages(args, scanner=main_scanner)

        details_scanner = Scanner()
        for product in crawl(num_pages, scanner=main_scanner):
            product = crawl_details(product = product, scanner = details_scanner)
            save_to_mongo(product=product, collection=coll)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='usedproducts',
        description='Crawler for userdproducts.com',
        )
    parser.add_argument('--log', '-l', choices=['DEBUG','INFO','WARN','ERROR'],
                        help='loglevel: DEBUG, INFO, WARN, ERROR (default: ERROR)')

    parser.add_argument('--max_pages', '-p', type=int, help='maximum number of pages to load', default=sys.maxsize)
    parser.add_argument('--reset', '-r', action='store_true', help='reset the database before crawling, implies --crawl')
    parser.add_argument('--crawl', '-c', action='store_true', help='crawl the web')
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
