import requests
from ip_pool.auto_pool import get_ip
from ip_pool.agents import agents
from bs4 import BeautifulSoup
import random
import warnings
import Logger
import re
import logging
import hashlib


warnings.filterwarnings("ignore")
logger = Logger.get_logger(logging.INFO)

_GOOGLEID = hashlib.md5(str(random.random()).encode("utf-8")).hexdigest()[:16]
_COOKIES = {"GSP": "ID={0}:CF=4".format(_GOOGLEID)}
_HEADERS = {
    "accept-language": "en-US, en",
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml'
}
_HOST = "https://google.com"
_SEARCH = "/search?num=20&q={0}"
_SESSION = requests.Session()
_PROXIES = get_ip()


def _get_page(pagerequest):
    resp = _SESSION.get(
        pagerequest,
        headers=_HEADERS,
        cookies=_COOKIES,
        # proxies=_PROXIES,
        # verify=False,
    )
    resp.encoding = "utf-8"
    if resp.status_code == 200:
        return resp.text
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def _make_soup(pagerequest):
    html = _get_page(pagerequest)
    return BeautifulSoup(html, "lxml")


class Spider(object):
    def __init__(self):
        self.monitor = 0

    def get_email_and_phone(self, keywords):
        try:
            url_ep = _SEARCH.format(requests.utils.quote(keywords))
            soup = _make_soup(pagerequest=_HOST + url_ep)
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
            question = "What country is %s in?" % affiliation
            url_country = _SEARCH.format(requests.utils.quote(question))
            soup = _make_soup(_HOST + url_country)
            tag_results = soup.select("div[class='Z0LcW']")
            return tag_results[0].getText() if len(tag_results) > 0 else ''
        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR"

    def get_address(self, affiliation):
        try:
            question = "Where is %s located?" % affiliation
            url_address = _SEARCH.format(requests.utils.quote(question))
            soup = _make_soup(_HOST + url_address)
            tag_results = soup.select("div[class='Z0LcW']")
            return tag_results[0].getText() if len(tag_results) > 0 else ''
        except Exception as e:
            logger.error("%d | %s" % (self.monitor, str(e)))
        finally:
            return "ERROR"

    def get_position(self, keywords):
        try:
            url_position = _SEARCH.format(requests.utils.quote(keywords))
            soup = _make_soup(_HOST + url_position)
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

