#!/usr/bin/env python
import argparse
import time
from multiprocessing import Process
import multiprocessing
import os
import urllib3
import logging
import sys
import pymongo
import psutil

from lib.scanner import Scanner
from lib.product import Product, productFromMongo

# enable only after pip install -U memory_profiler
# from memory_profiler import profile

def crawl(num_pages):
    scanner = Scanner()
    for i in range(1, num_pages + 1):
        page_uri = f"https://www.usedproducts.nl/page/{i}/?s&post_type=product&vestiging=0"
        if i % 50 == 0:
            scanner = Scanner()
        # print(f"Loading summary page {i}")
        try:
            for product in scanner.scan(page_uri):
                yield product
        except Exception as e:
            print(f"### Error: Failed loading summary page {i}: {page_uri} with error {str(e)}")
            scanner = Scanner()

def crawl_details(q_incoming: multiprocessing.Queue, q_outgoing: multiprocessing.Queue):
    scanner = Scanner()
    count = 0
    while(True):
        incoming = q_incoming.get()
        count += 1
        if count % 50 == 0:
            scanner = Scanner()
        if type(incoming) is Product:
            product = incoming
            # print(f"Loading product: {product.name}")
            try:
                product.desc, product.short_desc = scanner.scan_details(product.link)
                product.fill_derived()
                q_outgoing.put(product)
            except Exception as e:
                scanner = Scanner()
                print(f"### Error: Failed loading product {product.link} with error {str(e)}")
        if type(incoming) is str:
            print("Exiting crawler process")
            return
    
    # return product

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

    coll = get_mongo()

    if args.empty:
        coll.delete_many({ })

    if args.crawl or args.empty:
        page_scanner = Scanner()
        num_pages = get_num_pages(args, scanner=page_scanner)

        ctx = multiprocessing.get_context('spawn')
        queue_crawl = ctx.Queue(maxsize=100)
        queue_save = ctx.Queue()
        save_process = Process(target=save_product, args=(queue_save,))
        save_process.start()
        processes = [Process(target=crawl_details, args=(queue_crawl,queue_save,)) for i in range(8)]
        for process in processes:
            process.start()

        active_processes = len(processes)

        for product in crawl(num_pages):
            # print(f"Putting product: {product.name}")
            while queue_crawl.full():
                print(f"Going for a break ... mem: {psutil.virtual_memory().percent}")
                time.sleep(4.0)
            if psutil.virtual_memory().percent > 80:
                print("#### MEMORY WARNING #####")
                if active_processes > 1:
                    active_processes -= 1
                    queue_crawl.put("finish")

            queue_crawl.put(product)

        for process in range(active_processes):
            queue_crawl.put("finish")
        for process in processes:
            process.join()
        queue_save.put("finish")
        save_process.join()
    else: 
        if args.refresh:
            for mongo_product in coll.find():
                filter = { 'id': mongo_product._id }
                product = productFromMongo(mongo_product)
                product.fill_derived()
                coll.update_one(filter, product.__dict__)



def parse_args():
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
    return (True, args)


def config_env():
    # some pages are self-signed by ABN AMRO, and we don't want to see all the warnings about those
    urllib3.disable_warnings()

    os.environ['PATH'] = f"{os.environ['PATH']}:{os.getcwd()}"


if __name__ == "__main__":
    main()
