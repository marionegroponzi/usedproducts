#!/usr/bin/env python
import argparse
import time

import multiprocessing
import os
import urllib3
import logging
import sys
from lib.process_manager import ProcessManager
from lib.crawler import Crawler
from lib.db_manager import DBManager

# enable only after pip install -U memory_profiler
# from memory_profiler import profile

def handle_main_process(pm:ProcessManager, queue_stop:multiprocessing.Queue):
    value = None
    if queue_stop.empty():
        print("Checking system status")
        pm.check_system_status()
        time.sleep(10.0)
    else:
        value = queue_stop.get()
        print(f"Shutting down: {value}")
    return value

# @profile
def main():
    args = parse_args()
    config_env()
    db_manager=DBManager()
    if args.refresh:
            DBManager().refresh()
            return
    
    if args.empty: db_manager.clear()

    num_pages = Crawler.get_num_pages(args.max_pages)
    
    if args.crawl or args.empty:
        ctx = multiprocessing.get_context('spawn')
        queue_stop = ctx.Queue()
        pm = ProcessManager(q_stop=queue_stop, num_pages=num_pages)
        pm.start()
        value = None
        while(value != "Finish"):
            value = handle_main_process(pm=pm, queue_stop=queue_stop)
        pm.stop()

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
