import sys
import time
from multiprocessing import Process, Queue, Lock, Value
from Queue import Empty

class Done(Exception):
    pass

class Producer(object):
    def produce(self):
        pass # abstract, must return data or raise Done

class Consumer(object):
    def consume(self, data):
        pass # abstract

class Director(object):
    def __init__(self, producer, consumer):
        self.producer = producer
        self.consumer = consumer
        self.queue = Queue()
        self.prod_proc = Process(target = self.produce)
        self.prod_proc.daemon = True
        self.lock = Lock()
        self.done = Value('b')
        self.done.value = 0

    def start(self):
        self.prod_proc.start()

    def step(self):
        self.lock.acquire()
        done = (self.done.value != 0)
        self.lock.release()
        if done:
            raise Done
        try:
            data = self.queue.get(block = True, timeout = 1.0)
            self.consumer.consume(data)
        except Empty:
            pass

    def stop(self):
        self.prod_proc.join()

    def run(self):
        self.start()
        while True:
            try:
                self.step()
            except Done:
                break
        self.stop()
        
    def produce(self):
        try:
            while True:
                data = self.producer.produce()
                self.queue.put(data)
        except:
            self.lock.acquire()
            self.done.value = 1
            self.lock.release()
            self.queue.close()
            self.queue.join_thread()

class MyProducer(Producer):
    def __init__(self):
        self.counter = 0

    def produce(self):
        time.sleep(0.01)
        self.counter = self.counter + 1
        if self.counter > 1000:
            raise Done()
        return self.counter

class MyConsumer(Consumer):
    def __init__(self):
        pass

    def consume(self, data):
        sys.stdout.write('.')
        sys.stdout.flush()

if __name__ == '__main__':
    p = MyProducer()
    c = MyConsumer()
    d = Director(p, c)
    d.run()
