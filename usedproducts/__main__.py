#!/usr/bin/env python
import argparse
import json
import os
import urllib3
import logging

from lib.scanner import Scanner
from lib.products import ProductsEncoder

def crawl():
    print('>>>>>>>>>> usedproducts crawling start <<<<<<<<<<')
    scanner = Scanner()
    # num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    # for page in range(1,num_pages+1):
    for page in range(1,10):
        scanner.scan(f"https://www.usedproducts.nl/page/{page}/?s&post_type=product&vestiging=0")
    # print(ProductsEncoder().encode(scanner.products))
    scannedProducts = json.dumps(scanner.products, indent=4, cls=ProductsEncoder, ensure_ascii=False)
    print(scannedProducts)

    scanner.close()
    print('<<<<<<<<<< usedproducts crawling stop >>>>>>>>>>')

def analyze():
    print('>>>>>>>>>> usedproducts analysis start <<<<<<<<<<')

    print('>>>>>>>>>> usedproducts analysis stop <<<<<<<<<<')

def main():
    (success, args) = parse_args()
    if not success:
        return
    config_env()
    crawl()

def parse_args():
    parser = argparse.ArgumentParser(
        prog='usedproducts',
        description='Crawler and analyzer for userdproducts.com',
        )
    parser.add_argument('--log', '-l', choices=['DEBUG','INFO','WARN','ERROR'],
                        help='loglevel: DEBUG, INFO, WARN, ERROR (default: ERROR)')
    parser.add_argument('--load-file', '-f', type=argparse.FileType('r'), help='analyze data from a json file')
    parser.add_argument('--save-file', '-s', type=argparse.FileType('w'), help='save data to a json file')
    args = parser.parse_args()
    if args.log is not None:
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
