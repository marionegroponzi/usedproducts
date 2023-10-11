#!/usr/bin/env python
import argparse

import multiprocessing
import os
from time import sleep
import urllib3
import logging
import sys
import pymongo

from lib.scanner import Scanner
from lib.product import Product, productFromMongo
from lib.process_manager import ProcessManager

# enable only after pip install -U memory_profiler
# from memory_profiler import profile

def update_verified_date(product: Product):
    coll = get_mongo()
    coll.update_one({"link": product.link},{"$set": {"verified": product.verified }})

def already_stored(product: Product):
    coll = get_mongo()
    already_stored = coll.find_one({ "link": product.link })
    return already_stored != None

def crawl(q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue, num_pages, q_stop: multiprocessing.Queue):
    scanner = Scanner()
    count = 0
    while(True):
        incoming = q_incoming.get()
        if type(incoming) is int:
            print(f"incoming crawl: {incoming}")
            count += 1
            if count % 50 == 0: scanner = Scanner()
            index = incoming            
            page_uri = f"https://www.usedproducts.nl/page/{index}/?s&post_type=product&vestiging=0"
            # print(f"Loading summary page {incoming}")
            try:
                for product in scanner.scan(page_uri):
                    if already_stored(product):
                        print(f"already stored {product.name}")
                        product.set_verified_date()
                        update_verified_date(product=product)
                    else:
                        print(f"putting out {index}")
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

def crawl_details(q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue):
    scanner = Scanner()
    count = 0
    while(True):
        incoming = q_incoming.get()
        if type(incoming) is Product:
            print(f"incoming details: {incoming.name}")
            count += 1
            if count % 50 == 0: scanner = Scanner()            
            product = incoming
            # print(f"Loading product: {product.name}")
            try:
                product.desc, product.short_desc = scanner.scan_details(product.link)
                product.fill_derived()
                product.set_created_date()
                product.set_verified_date()
                q_outgoing.put(product)
            except Exception as e:
                scanner = Scanner()
                print(f"### Error: Failed loading product {product.link} with error {str(e)}")
        if type(incoming) is str:
            print("Exiting details crawler process")
            return

def save_product(q_incoming: multiprocessing.Queue):
    coll = get_mongo()
    while(True):
        incoming = q_incoming.get()
        if type(incoming) is Product:
            # print(f"Saving product {incoming.name}")
            save_to_mongo(incoming, coll)
        if type(incoming) is str:
            print("Exiting save process")
            return

def save_to_mongo(product, collection):
    if collection is not None:
        # pay attention that inserting the product modifies it. If you need to return it, copy the dict first
        d = product.__dict__
        collection.insert_one(d)

def get_mongo() -> pymongo.collection.Collection:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    coll = client.usedproducts.products
    return coll

def get_num_pages(args):
    scanner = Scanner()
    num_pages = scanner.get_num_pages("https://www.usedproducts.nl/page/1/?s&post_type=product&vestiging=0")
    scanner.accept_cookies()
    return min(num_pages, args.max_pages)

# @profile
def main():
    args = parse_args()
    config_env()

    coll = get_mongo()

    if args.empty: coll.delete_many({ })

    if args.crawl or args.empty:
        num_pages = get_num_pages(args)
        ctx = multiprocessing.get_context('spawn')
        queue_stop = ctx.Queue()
        pm = ProcessManager(crawl_page_fn=crawl, save_fn=save_product, crawl_details_fn=crawl_details, num_pages=num_pages, q_stop=queue_stop)
        pm.start()
        value=queue_stop.get()
        print(value)
        pm.stop()
    else: 
        if args.refresh:
            for mongo_product in coll.find():
                filter = { 'id': mongo_product._id }
                product = productFromMongo(mongo_product)
                product.fill_derived()
                coll.update_one(filter, product.__dict__)

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
