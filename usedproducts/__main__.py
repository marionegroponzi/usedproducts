#!/usr/bin/env python
import argparse
import json
import os
import urllib3
import logging
import sys

from lib.scanner import Scanner
from lib.products import ProductsContainer

def crawl(max_pages):
    scanner = Scanner()
    num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    scanner.accept_cookies()
    for page in range(1,min(num_pages, max_pages)+1):
        scanner.scan(f"https://www.usedproducts.nl/page/{page}/?s&post_type=product&vestiging=0")
    scanner.close()
    return scanner.products_container

def crawl_details(products):
    scanner = Scanner()
    for product in products:
        product.details = scanner.scan_details(product.link)

    scanner.close()

def load(filename) -> ProductsContainer:
    content = open(filename, "r").read()
    d = json.loads(content)
    return ProductsContainer(d)

def main():
    (success, args) = parse_args()
    if not success:
        print("Something wrong with the arguments")
        return
    config_env()

    # if loading a file we assum one wants to add all derived data
    # else we assume one want to store just the basics
    if args.load:
        products_container = load(args.load.name)
        products_container.fill_derived()
    else:
        products_container = crawl(args.max_pages)
        crawl_details(products_container.products)
        
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
    parser.add_argument('--load', '-f', type=argparse.FileType('r'), help='analyze data from a json file')
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
