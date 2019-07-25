import os
import re
import signal
import subprocess
import time

from multiprocessing import Process, Value, Queue

import chardet
from setting import dirname

class Spider(object):

    def __init__(self, spider, opts=''):
        self.process = None
        self.count = Value('i', 0)
        self.pid = Value('i', -1)
        self.q = Queue()
        self.spider = spider
        self.opts = opts

    # 运行爬虫
    def run(self, count, q, pid):
        p = subprocess.Popen('scrapy crawl ' + self.spider + self.opts, cwd=dirname + '/weibosearch', shell=True,
                             stderr=subprocess.PIPE)
        pid.value = p.pid
        flag = False
        while True:
            line = p.stderr.readline()
            try:
                line = line.decode(chardet.detect(line)['encoding'])
                if re.match('{\'', line):
                    flag = True
                    q.put('\r\n-------------------------------------------------------\r\n')
                elif re.match('\d', line):
                    flag = False
                if flag:
                    q.put(line)
                temp = re.search(r'get total count:(\d+)', line).group(1)
                count.value = int(temp)
            except:
                pass
            if p.poll() == 0:
                count.value = -1

    # 开启爬虫
    def start(self):
        if self.process:
            return
        self.process = Process(target=self.run, args=(self.count, self.q, self.pid))
        self.process.start()

    # 关闭爬虫
    def stop(self):
        if self.pid.value > 0:
            os.system('taskkill /f /pid ' + str(self.pid.value) + ' /t >> nul')
        if self.process:
            self.process.terminate()
            self.process = None


if __name__ == '__main__':
    s = Spider('weibo')
    s.start(' -a keyword=非洲瘟疫')
    time.sleep(5)
    # s.stop()
