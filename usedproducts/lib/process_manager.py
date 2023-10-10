import multiprocessing
from multiprocessing import Process
import time

import psutil

class ProcessManager(object):
    def __init__(self, save_fn, crawl_page_fn, crawl_details_fn, num_pages: int):
        ctx = multiprocessing.get_context('spawn')
        self.num_pages = num_pages
        self.queue_crawl_pages = ctx.Queue()
        self.queue_crawl_details = ctx.Queue(maxsize=100)
        self.queue_save = ctx.Queue()
        self.save_process = Process(target=save_fn, args=(self.queue_save,))
        self.active_crawl_pages_processes = 12
        self.active_crawl_details_processes = 12
        self.crawl_details_processes = [Process(target=crawl_details_fn, args=(self.queue_crawl_details, self.queue_save,)) for i in range(self.active_crawl_details_processes)]
        self.crawl_pages_processes = [Process(target=crawl_page_fn, args=(self.queue_crawl_pages, self.queue_crawl_details,)) for i in range(self.active_crawl_pages_processes)]

    def start(self):
        for process in self.crawl_pages_processes:
            process.start()
        self.save_process.start()
        for process in self.crawl_details_processes:
            process.start()
        for i in range(self.num_pages): self.queue_crawl_pages.put(i)
        

    def stop(self):
        for process in range(self.active_crawl_details_processes):
            self.queue_crawl_details.put("finish")
        for process in range(self.active_crawl_pages_processes):
            self.queue_crawl_pages.put("finish")   
        self.queue_save.put("finish")         
        for process in self.crawl_details_processes:
            process.join()
        for process in self.crawl_pages_processes:
            process.join()        
        self.save_process.join()

    def check_system_status(self):
        while self.queue_crawl_details.full():
            print(f"Taking a break ... mem: {psutil.virtual_memory().percent}")
            time.sleep(8.0)
        if psutil.virtual_memory().percent > 80:
            print("#### MEMORY WARNING #####")
            if active_processes > 1:
                active_processes -= 1
                self.queue_crawl_details.put("finish")