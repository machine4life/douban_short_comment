import threading
import time


def test(i):
    time.sleep(10/i)
    print i


for i in range(1, 10):
    threading.Thread(target=test, args=(i,)).start()

