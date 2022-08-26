import requests

class WebsiteAnalyser:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        self.user_agent_header = {"User-agent": self.user_agent}
        session = requests.Session()
        session.headers.update({'User-Agent': 'Custom user agent'})

        with open("resources/domain_tlds.txt", "r") as f:
            f = f.read().split("\n")

        self.domain_tlds = f

    def check_url_up(self, url, check_status_code=True):
        try:
            request = self.session.get(url, headers=self.user_agent_header)
            if check_status_code:
                if request.status_code > 199 and request.status_code < 300:
                    return request.url
                else:
                    return False
            else:
                request.url
        except:
            return False

    def is_valid_tld(self, url_or_mail):
        return url_or_mail.split(".")[-1].upper() not in self.domain_tlds

    def get_domainname(self, url_or_mail):
        domain = url_or_mail
        try:
            domain = domain.split("//")[1]
        except:
            pass

        try:
            domain = domain.split("www.")[1]
        except:
            pass

        return domain

    def sanitizeurls(self, urls, must_be_unique=True):
        for url in urls:
            if url.split(".")[-1].isnumeric() or url.split(".")[-1].upper() not in self.domain_tlds or url == "":
                print("numericaly invalid or wrong ending " + url)
                urls.remove(url)

        for url in urls:
            result = self.check_url_up(url)
            if result != False:
                continue

            result = self.check_url_up("https://" + url)
            if result != False:
                urls[urls.index(url)] = result
                continue
            result = self.check_url_up("http://" + url)
            if result != False:
                urls[urls.index(url)] = result
                continue
            result = self.check_url_up("https://" + url.replace("www.", ""))
            if result != False:
                urls[urls.index(url)] = result
                continue
            result = self.check_url_up("http://" + url.replace("www.", ""))
            if result != False:
                urls[urls.index(url)] = result
                continue
        
        if must_be_unique:
            urls2 = []
            for url in urls:
                if not any([url2.endswith(self.get_domainname(url)) for url2 in urls2]):
                    urls2.append(url)
        else:
            urls2 = urls
    
        return urls2