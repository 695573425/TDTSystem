import sys
import time
from multiprocessing import Process

from cookiespool.api import app
from cookiespool.config import *
from cookiespool.generator import *
from cookiespool.tester import *


class Scheduler(object):
    @staticmethod
    def valid_cookie(cycle=CYCLE):
        while True:
            print('Cookies检测进程开始运行')
            try:
                for website, cls in TESTER_MAP.items():
                    tester = eval(cls + '(website="' + website + '")')
                    tester.run()
                    print('Cookies检测完成')
                    del tester
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)
    
    @staticmethod
    def generate_cookie(cycle=CYCLE):
        while True:
            print('Cookies生成进程开始运行')
            try:
                for website, cls in GENERATOR_MAP.items():
                    generator = eval(cls + '(website="' + website + '")')
                    generator.run()
                    print('Cookies生成完成')
                    generator.close()
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)
    
    @staticmethod
    def api():
        print('API接口开始运行')
        app.run(host=API_HOST, port=API_PORT)

    def run(self, flag, generator, valid, api):

        if isinstance(generator, bool):
            global GENERATOR_PROCESS
            GENERATOR_PROCESS = generator
        if isinstance(valid, bool):
            global VALID_PROCESS
            VALID_PROCESS = valid
        if isinstance(api, bool):
            global API_PROCESS
            API_PROCESS = api

        if GENERATOR_PROCESS:
            generate_process = Process(target=Scheduler.generate_cookie)
            generate_process.start()

        if VALID_PROCESS:
            valid_process = Process(target=Scheduler.valid_cookie)
            valid_process.start()

        if API_PROCESS:
            api_process = Process(target=Scheduler.api)
            api_process.start()

        while True:
            if flag.value:
                if GENERATOR_PROCESS:
                    generate_process.terminate()
                if VALID_PROCESS:
                    valid_process.terminate()
                if API_PROCESS:
                    api_process.terminate()
                break


