#!/usr/bin/env python
import argparse
import os
import urllib3
import logging

from lib.scanner import Scanner

def crawl():
    print('>>>>>>>>>> usedproducts crawling start <<<<<<<<<<')
    scanner = Scanner()
    # num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    # for page in range(1,num_pages+1):
    for page in range(1,10):
        scanner.scan(f"https://www.usedproducts.nl/page/{page}/?s&post_type=product&vestiging=0")
    print(scanner.products.toJSON())
    scanner.close()
    print('<<<<<<<<<< usedproducts crawling stop >>>>>>>>>>')

def analyze():
    print('>>>>>>>>>> usedproducts analysis start <<<<<<<<<<')

    print('>>>>>>>>>> usedproducts analysis stop <<<<<<<<<<')

def main():
    (success, command) = parse_args()
    if not success:
        return
    config_env()
    match command:
        case 'crawl':
            crawl()
        case 'analyze':
            analyze()
        case _:
            print('Command unknown')

def parse_args():
    parser = argparse.ArgumentParser(
        prog='usedproducts',
        description='Crawler and analyzer for userdproducts.com',
        )
    parser.add_argument('--log', '-l', choices=['DEBUG','INFO','WARN','ERROR'],
                        help='loglevel: DEBUG, INFO, WARN, ERROR (default: ERROR)')
    parser.add_argument('command', choices=['crawl','analyze'], help='select either crawl or analyze')
    args = parser.parse_args()
    if args.log is not None:
        numeric_level = getattr(logging, args.log.upper())
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.basicConfig(level=numeric_level)
    return (True, args.command)


def config_env():
    # some pages are self-signed by ABN AMRO, and we don't want to see all the warnings about those
    urllib3.disable_warnings()

    os.environ['PATH'] = f"{os.environ['PATH']}:{os.getcwd()}"


if __name__ == "__main__":
    main()
