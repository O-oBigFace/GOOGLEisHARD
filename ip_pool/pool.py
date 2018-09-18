import requests
import time


class Pool(object):
    instance = None

    def __init__(self):
        self.__ip_list = []
        self.__time_tag = time.time()

    def get_ip(self):
        if len(self.__ip_list) < 1 or self.__count + 2 > len(self.__ip_list) or time.time() - self.__time_tag > 600:
            self.__get_ip_list()
        self.__count += 1
        return self.__ip_list[self.__count]

    def __get_ip_list(self):
        self.__time_tag = time.time()
        self.__count = -1
        r = requests.get("http://api3.xiguadaili.com/ip/?tid=559660784928254&num=20&category=2")
        r.encoding = "utf-8"
        self.__ip_list = [{
            "http": "http://" + ip.strip(),
            "https": "https://" + ip.strip(),
        } for ip in r.text.split("\n")]




