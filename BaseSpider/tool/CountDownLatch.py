import threading


class CountDownLatch:

    def __init__(self, count):
        self.count = count
        self.condition = threading.Condition()

    def wait(self):
        try:
            self.condition.acquire()
            while self.count > 0:
                self.condition.wait()
        finally:
            self.condition.release()

    def count_down(self):
        try:
            self.condition.acquire()
            self.count -= 1
            self.condition.notifyAll()
        finally:
            self.condition.release()

    def get_count(self):
        return self.count

