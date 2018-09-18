import requests
from bs4 import BeautifulSoup
import random
from ip_pool.agents import agents
import time
from multiprocessing import Lock

"""
    ip代理池
    实现的功能：
    1、 爬取ip代理网站的ip地址 约10~20页
    2、 利用计时器定期更新ip地址
    3、 由于程序的架构，此类对象的调用会写在spider类中，MyResquest将接受它的对象

    4、 不同的ip提供方式，随机选择和ip轮询等等
"""


def synchronized(func):
    func.__lock__ = Lock()

    def lock_function(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)


class IPProvider(object):
    instance = None

    def __init__(self, numopages=5):
        self.__numopages = numopages
        self.__ip_list = []
        self.__time_tag = time.time()
        self.__count = -1
        self.cold_start = True
        self.cold_ip = {}
        self.__cold_start()

    # @synchronized
    # def __new__(cls, *args, **kwargs):
    #     if cls.instance is None:
    #         cls.instance = super().__new__(cls)
    #         return cls.instance

    def __cold_start(self):
        ty = input("type: ")
        ip = input("ip: ")
        port = input("port: ")
        self.cold_ip[ty] = ty + "://" + ip + ":" + port

    def get_ip(self):
        if len(self.__ip_list) < 1 or self.__count > len(self.__ip_list) or time.time() - self.__time_tag > 600:
            self.__get_ip_list()
        self.__count += 1

        return {
            self.__ip_list[self.__count][0]: self.__ip_list[self.__count][0] + "://" + self.__ip_list[self.__count][1] + ":" + self.__ip_list[self.__count][2]
                }

    def __get_ip_list(self):
        self.__time_tag = time.time()
        self.__count = -1
        for i in range(1, self.__numopages + 1):
            soup = self.__get_soup('http://www.xicidaili.com/nn/' + str(i))
            # print(soup)
            # 每一段ip
            for tr in soup.find_all("tr"):
                item = tr.find_all("td")
                if len(item) > 6:
                    self.__ip_list.append((item[5].getText().lower(), item[1].getText(), item[2].getText()))

    def __get_soup(self, url):
        headers = {
            "User-Agent": random.choice(agents),
        }
        r = None
        if self.cold_start:
            try:
                r = requests.get(url, headers=headers, proxies=self.cold_ip)
            except Exception as e:
                print(e)
            self.cold_start = True
        else:
            max_tries = 0
            while r is None and max_tries < 6:
                r = requests.get(url, headers=headers, proxies= self.formalize(random.choice(self.__ip_list)))
                max_tries += 1
        if r is None:
            raise NotImplemented
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "lxml")

    def formalize(self, tp):
        return {
            tp[0]: tp[0] + "://" + tp[1] + ":" + tp[2]
                }


if __name__ == "__main__":
    ipp = IPProvider(5)
    ip = IPProvider(5)
    print(ipp.get_ip())
