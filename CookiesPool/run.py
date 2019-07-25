import sys
from setting import dirname
sys.path.append(dirname + '/CookiesPool')

from cookiespool.scheduler import Scheduler

from multiprocessing import Process, Value

class Cookies(object):
    if_stop = Value('b', False)

    # 开启Cookies池
    @staticmethod
    def start(generate=None, valid=None, api=None):
        Cookies.if_stop.value = False
        s = Scheduler()
        p = Process(target=s.run, args=(Cookies.if_stop, generate, valid, api))
        p.start()

    # 关闭Cookies池
    @staticmethod
    def stop():
        Cookies.if_stop.value = True


if __name__ == '__main__':
    Cookies.start()
