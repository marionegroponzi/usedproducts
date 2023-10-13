#!/usr/bin/env python
import argparse
import time

import multiprocessing
import os
import urllib3
import logging
import sys
import pymongo

from lib.scanner import Scanner
from lib.product import Product, productFromMongo
from lib.process_manager import ProcessManager
from lib.crawler import Crawler
from lib.db_manager import DBManager

# enable only after pip install -U memory_profiler
# from memory_profiler import profile




def handle_main_process(pm:ProcessManager, queue_stop:multiprocessing.Queue):
    if queue_stop.empty():
        print("Checking system status")
        pm.check_system_status()
        time.sleep(10.0)
    else:
        value = queue_stop.get()
        print(f"Shutting down: {value}")

# @profile
def main():
    args = parse_args()
    config_env()
    db_manager=DBManager()
    if args.empty: db_manager.clear()

    if args.crawl or args.empty:
        crawler = Crawler(args)
        ctx = multiprocessing.get_context('spawn')
        queue_stop = ctx.Queue()
        pm = ProcessManager(crawler=crawler, db_manager=db_manager, q_stop=queue_stop)
        # pm = ProcessManager(crawl_page_fn=crawl, save_fn=save_product, crawl_details_fn=crawl_details, num_pages=num_pages, q_stop=queue_stop)
        pm.start()
        value = None
        while(value != "Finish"):
            handle_main_process()
        pm.stop()
    else: 
        pass
        # if args.refresh:
        #     for mongo_product in coll.find():
        #         filter = { 'id': mongo_product._id }
        #         product = productFromMongo(mongo_product)
        #         product.fill_derived()
        #         coll.update_one(filter, product.__dict__)

def parse_args():
    try:
        parser = argparse.ArgumentParser(
            prog='usedproducts',
            description='Crawler for userdproducts.com',
            )
        parser.add_argument('--log', '-l', choices=['DEBUG','INFO','WARN','ERROR'],
                            help='loglevel: DEBUG, INFO, WARN, ERROR (default: ERROR)')

        parser.add_argument('--max_pages', '-p', type=int, help='maximum number of pages to load', default=sys.maxsize)
        parser.add_argument('--empty', '-e', action='store_true', help='empty the database before crawling, implies --crawl')
        parser.add_argument('--crawl', '-c', action='store_true', help='crawl the web')
        parser.add_argument('--refresh', '-r', action='store_true', help='refresh the database without crawling')
        args = parser.parse_args()
        if args.log:
            numeric_level = getattr(logging, args.log.upper())
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % args.loglevel)
            logging.basicConfig(level=numeric_level)
        return args
    except:
        print("### Error: Something wrong with the arguments")
        exit(-1)


def config_env():
    urllib3.disable_warnings()
    os.environ['PATH'] = f"{os.environ['PATH']}:{os.getcwd()}"


if __name__ == "__main__":
    main()
