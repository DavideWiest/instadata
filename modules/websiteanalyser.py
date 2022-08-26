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

    def sanitizeurls(self, urls):
        for url in urls:
            if url.split(".")[-1].isnumeric() or url.split(".")[-1].upper() not in self.domain_tlds or url == "":
                urls.remove(url)

        for url in urls:
            result = self.check_url_up(url)
            if result != False:
                continue
            
            if url.startswith("www.") or (url.startswith("https://") == False and url.startswith("http://") == False):
                result = self.check_url_up("http://" + url)
                if result != False:
                    urls[urls.index(url)] = result
                    continue

                result = self.check_url_up("https://" + url)
                if result != False:
                    urls[urls.index(url)] = result
                    continue
            else:
                if url.startswith("https://"):
                    result = self.check_url_up(url.replace("https://", "http://"))
                    if result != False:
                        urls[urls.index(url)] = result
                        continue

                elif url.startswith("http://"):
                    result = self.check_url_up(url.replace("https://", "http://"))
                    if result != False:
                        urls[urls.index(url)] = result
                        continue

            urls.remove(url)

        return urls