#!/usr/bin/env python
import argparse
import json
import os
import urllib3
import logging

from lib.scanner import Scanner

def crawl():
    scanner = Scanner()
    num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    scanner.accept_cookies()
    # for page in range(1,num_pages+1):
    for page in range(1,2):
        scanner.scan(f"https://www.usedproducts.nl/page/{page}/?s&post_type=product&vestiging=0")
    scanner.close()
    return scanner.products_container

def crawl_details(products):
    scanner = Scanner()
    for product in products:
        product.details = scanner.scan_details(product.link)

    scanner.close()

def load(filename):
    content = open(filename, "r").read()
    return json.loads(content)

def main():
    (success, args) = parse_args()
    if not success:
        print("Something wrong with the arguments")
        return
    config_env()

    if args.load:
        products_container = load(args.load.name)
    else:
        products_container = crawl()
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
