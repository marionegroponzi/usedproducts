import multiprocessing
from multiprocessing import Process
import time

import psutil

class ProcessManager(object):
    def __init__(self, save_fn, crawl_fn):
        ctx = multiprocessing.get_context('spawn')
        self.queue_crawl = ctx.Queue(maxsize=100)
        self.queue_save = ctx.Queue()
        self.save_process = Process(target=save_fn, args=(self.queue_save,))
        self.active_processes = 12
        self.processes = [Process(target=crawl_fn, args=(self.queue_crawl, self.queue_save,)) for i in range(self.active_processes)]


    def start(self):
        self.save_process.start()
        for process in self.processes:
            process.start()

    def stop(self):
        for process in range(self.active_processes):
            self.queue_crawl.put("finish")
        for process in self.processes:
            process.join()
        self.queue_save.put("finish")
        self.save_process.join()

    def check_system_status(self):
        while self.queue_crawl.full():
            print(f"Taking a break ... mem: {psutil.virtual_memory().percent}")
            time.sleep(8.0)
        if psutil.virtual_memory().percent > 80:
            print("#### MEMORY WARNING #####")
            if active_processes > 1:
                active_processes -= 1
                self.queue_crawl.put("finish")