proxy_host = "proxy.crawlera.com"
proxy_port = "8010"
proxy_auth = "c3dad299d5bb46b785fda38e8322c5e4:"


def get_ip():
    return {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
            "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
