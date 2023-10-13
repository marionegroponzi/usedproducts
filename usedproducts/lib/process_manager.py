from lib.db_manager import DBManager
import multiprocessing
from multiprocessing import Process
import psutil
from lib.crawler import Crawler

def dbsave(q_save: multiprocessing.Queue):
    db_manager = DBManager()
    db_manager.save_product(q_save)

def crawldetails(queue_crawl_details: multiprocessing.Queue, queue_save: multiprocessing.Queue):
    crawler = Crawler()
    crawler.crawl_details(queue_crawl_details, queue_save)

def crawlpage(queue_crawl_pages: multiprocessing.Queue, queue_crawl_details: multiprocessing.Queue, q_stop: multiprocessing.Queue):
    crawler = Crawler()
    crawler.crawl(queue_crawl_pages, queue_crawl_details, q_stop)

class ProcessManager(object):
    def __init__(self, q_stop):
        ctx = multiprocessing.get_context('spawn')
        self.queue_crawl_pages = ctx.Queue()
        self.queue_crawl_details = ctx.Queue(maxsize=200)
        self.queue_save = ctx.Queue()
        self.save_process = Process(target=dbsave, args=(self.queue_save,))
        self.active_crawl_pages_processes = 12
        self.active_crawl_details_processes = 12
        self.crawl_details_processes = [Process(target=crawldetails, args=(self.queue_crawl_details, self.queue_save,)) for _ in range(self.active_crawl_details_processes)]
        self.crawl_pages_processes = [Process(target=crawlpage, args=(self.queue_crawl_pages, self.queue_crawl_details, q_stop, )) for _ in range(self.active_crawl_pages_processes)]
        # crawler.pm = self

    def start(self):
        # for process in self.crawl_pages_processes:
        #     process.start()
        self.save_process.start()
        # for process in self.crawl_details_processes:
        #     process.start()
        # for i in range(self.num_pages): self.queue_crawl_pages.put(i)
        
    def stop(self):
        # for process in range(self.active_crawl_pages_processes):
        #     self.queue_crawl_pages.put("finish")   
        # for process in self.crawl_pages_processes:
        #     process.join()
        # for process in range(self.active_crawl_details_processes):
        #     self.queue_crawl_details.put("finish")               
        # for process in self.crawl_details_processes:
        #     process.join() 
        self.queue_save.put("finish")      
        self.save_process.join()

    def check_system_status(self):
        if psutil.virtual_memory().percent > 80:
            print("#### MEMORY WARNING #####")
            # Kill on process per type when memory seems under pressure
            if self.active_crawl_pages_processes > 1:
                self.active_crawl_pages_processes -= 1
                self.crawl_pages_processes.put("finish")            
            if self.active_crawl_details_processes > 1:
                self.active_crawl_details_processes -= 1
                self.queue_crawl_details.put("finish")