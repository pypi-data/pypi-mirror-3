'''
Eleves -- Python Threading For Human
'''
import threading
import Queue
from functools import partial

queue = Queue.Queue()
threads = []

class Elf(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            job = self.queue.get()
            job()
            self.queue.task_done()

def run(num):
    for i in range(num):
        threads.append(Elf(queue))
        threads[-1].setDaemon(True)
        threads[-1].start()

def put(func, *args, **kwargs):
    queue.put(partial(func, *args, **kwargs))

def join():
    queue.join()
