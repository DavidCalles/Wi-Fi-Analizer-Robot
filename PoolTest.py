import multiprocessing as mp
import datetime as dt
from datetime import datetime as dtdt
import time

myglob = "Glob_Ok"

def worker1(msg):
    tInit = dtdt.now()
    while (1):
        if(dtdt.now() - tInit > dt.timedelta(seconds=2)):
            tInit = dtdt.now()
            print(f"-- ONE: {msg}{myglob}")

def worker2(msg):
    tInit = dtdt.now()
    while (1):
        if(dtdt.now() - tInit > dt.timedelta(seconds=3)):
            tInit = dtdt.now()
            print(f"--------TWO: {msg}{myglob}")

def worker3(msg):
    tInit = dtdt.now()
    while (1):
        if(dtdt.now() - tInit > dt.timedelta(seconds=1)):
            tInit = dtdt.now()
            print(f"-------------- THREE: {msg}{myglob}")

def worker4(msg):
    tInit = dtdt.now()
    while (1):
        if(dtdt.now() - tInit > dt.timedelta(seconds=2)):
            tInit = dtdt.now()
            print(f"--------------------- FOUR: {msg}{myglob}")

def worker5(msg):
    tInit = dtdt.now()
    while (1):
        if(dtdt.now() - tInit > dt.timedelta(seconds=1)):
            tInit = dtdt.now()
            print(f"---------------------------- FIVE: {msg}{myglob}")


tInit = dtdt.now()
Index = 0
num_workers = 5
pool = mp.Pool(processes=num_workers)
pool.apply_async(worker1, args = ("HEY",))
pool.apply_async(worker2, args = ("HEY",))
pool.apply_async(worker3, args = ("HEY",))
pool.apply_async(worker4, args = ("HEY",))
pool.apply_async(worker5, args = ("HEY",))

while(1):
    if(dtdt.now() - tInit > dt.timedelta(seconds=1)):
        tInit = dtdt.now()
        print(f"Time: {Index}")
        Index+=1


pool.close()
pool.join()