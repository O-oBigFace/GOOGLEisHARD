import requests
from ip_pool.auto_pool import get_ip
from ip_pool.agents import agents
from bs4 import BeautifulSoup
import random
import warnings
import Logger
import re
import logging


warnings.filterwarnings("ignore")
logger = Logger.get_logger(logging.DEBUG)


class Spider(object):
    def __init__(self):
        self.ip = get_ip()
        self.url = 'https://google.com/search'
        self.monitor = 0

    def get_header(self):
        return {
            # "accept": "*/*",
            # "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            # "accept-encoding": "gzip, deflate, br",
            # "refer": "https://www.google.com/",
            # "x-client-data": "CIi2yQEIpbbJAQjEtskBCKmdygEI153KAQjZncoBCKOfygEIqKPKARj5pcoB",
            # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }

    def make_soup(self, payloads):
        print(self.url, payloads, self.ip)
        r = requests.get(
            self.url,
            params=payloads,
            # headers=self.get_header(),
            proxies=self.ip,
            verify=False,
        )
        logger.info(r.url)
        r.encoding = "utf-8"
        if r.status_code == 200:
            return BeautifulSoup(r.text)
        elif r.status_code == 503:
            raise Exception('Error: {0} {1}'.format(r.status_code, r.reason))
        else:
            raise Exception('Error: {0} {1}'.format(r.status_code, r.reason))

    # def make_soup(self, payloads):
    #     http = urllib3.ProxyManager(self.ip)
    #     r = http.request("GET",
    #                      "https://www.google.com/search",
    #                      fields=payloads,
    #                      )
    #     if r.status == 200:
    #         return r.data.decode("utf-8")
    #     else:
    #         raise Exception('Error: {0}'.format(r.status))

    def payloader(self, tp, content):
        identifier = "q"
        if tp in ["address"]:
            return {
                identifier: "Where is %s located?" % content.split(';')[0],
            }
        if tp in ["email", "phone", "email and phone"]:
            return {
                identifier: "%s and email and phone" % content,
            }
        if tp in ["country"]:
            return {
                identifier: "What country is %s in?" % content.split(';')[0],
            }
        if tp in ["position"]:
            return {
                "q": "%s and (professor or researcher or scientist)" % content,
            }

    # Search the address by affiliation.
    def get_address(self, affiliation):
        try:
            soup = self.make_soup(payloads=self.payloader("address", affiliation))
            tag_results = soup.select("div[class='Z0LcW']")
            return tag_results[0].getText() if len(tag_results) > 0 else ''
        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR"

    def get_email_and_phone(self, keywords):
        try:
            soup = self.make_soup(payloads=self.payloader("email", keywords))
            tag_results = soup.select("span[class='st']")
            results = {str(tr)
                           .replace(r"<em>", '')
                           .replace(r"</em>", '')
                           .replace(r"<wbr>", '')
                           .replace(r"</wbr>", '') for tr in tag_results}

            emailRegex = re.compile(r"""([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))""", re.VERBOSE)
            emailFilterRegex = re.compile(r"""^[Ee]-?mail""")
            phoneRegex = re.compile(
                r"""([Pp]hone|[Mm]obile|[Tt]el)[,:]?[\s/]*(\+\s?[\d]+[\s/]?)?(\([\d\-. ]+\)[\s/]{0,2})*(\d+[/.-]?[\s/]?)*""",
                re.VERBOSE)
            phoneFilterRegex = re.compile(r"""([Pp]hone|[Mm]obile|[Tt]el)[,:]?\s*""")

            email = str()
            phone = str()
            # 每一条摘要
            for r in results:
                pho = phoneRegex.search(r)
                pho_no = phoneFilterRegex.sub('', pho.group()).strip() if pho is not None else ''
                phone = pho_no if len(pho_no) > len(phone) else phone

                ems = [emailFilterRegex.sub('', e).strip() for a in emailRegex.findall(r) for e in a]
                for e in ems:
                    email = e if len(e) > len(email) else email
            return email, phone

        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR", "ERROR"

    def get_country(self, affiliation):
        try:
            soup = self.make_soup(payloads=self.payloader("country", affiliation))
            tag_results = soup.select("div[class='Z0LcW']")
            return tag_results[0].getText() if len(tag_results) > 0 else ''
        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR"

    def get_position(self, keywords):
        try:
            soup = self.make_soup(payloads=self.payloader("position", keywords))
            tag_results = soup.select("span[class='st']")
            results = {str(tr)
                           .replace(r"<em>", '')
                           .replace(r"</em>", '')
                           .replace(r"<wbr>", '')
                           .replace(r"</wbr>", '') for tr in tag_results}

            associateProfessorRegex = re.compile('''[Aa]ssociate\s+[Pp]rofessor''')
            assistantProfessorRegex = re.compile('''[Aa]ssistant\s+[Pp]rofessor''')
            professorRegex = re.compile('''[Pp]rofessor''')
            researcherRegex = re.compile('''[Rr]esearcher''')
            scientistRegex = re.compile('''[Ss]cientist''')

            # position需要设置优先级
            for r in results:
                if associateProfessorRegex.search(r):
                    return 'Associate Professor'

                if assistantProfessorRegex.search(r):
                    return 'Assistant Professor'

                if professorRegex.search(r):
                    return "Professor"

                if researcherRegex.search(r):
                    return 'Researcher'

                if scientistRegex.search(r):
                    return 'Scientist'
        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR"

