from modules.textanalyser import TextAnalyser, LocationHandler
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper
from modules.instadata import InstaData
from modules.websiteanalyser import ProxyChecker
import time

# username, password
ACCOUNTS_DATA = [
    ["seauser565", "seauser656"]
]

USERMAX = float("inf")
SLEEP_TIME = 7
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 2)
ANALYZE_PREVENTION = ("sleep reconnect proxy_reconnect", 3600 * 2.5)

if __name__ == "__main__":
    mm = MongoManager()
    ta = TextAnalyser()
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    pc = ProxyChecker()
    lh = LocationHandler()
    dh = DataHandler(mm, ta, ls, lh)

    id = InstaData(ACCOUNTS_DATA, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, ANALYZE_PREVENTION, mm, ta, ls, dh, pc)

    # gfl_filter = {"category": {"$in" ["Entrepreneur", "Public figure", "Product/service", "Real Estate Agent", "Retail company", "Local business", "Blogger", "Digital Creator"]}}
    gfl_filter = {"category": {"$nin": ["Artist", "Art", "Photographer", "Graphic Designer", "Digital creator", "Visual Arts"]}}
    id.make_list(use_log=True, db_reconnect=3600 * 4, gfl_filter=gfl_filter)

