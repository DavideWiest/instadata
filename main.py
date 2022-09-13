from modules.textanalyser import TextAnalyser, LocationHandler
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper
from modules.instadata import InstaData
import time

# username, password, proxy
ACCOUNTS_DATA = [
    ["seauser565", "seauser656", ""]
]

USERMAX = float("inf")
SLEEP_TIME = 10
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 2)
ANALYZE_PREVENTION = ("sleep reconnect", 3600 * 2.5)

if __name__ == "__main__":
    mm = MongoManager()
    ta = TextAnalyser()
    lh = LocationHandler([user[2] for user in ACCOUNTS_DATA if user[2] != ""])
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    dh = DataHandler(mm, ta, ls, lh)

    id = InstaData(ACCOUNTS_DATA, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, ANALYZE_PREVENTION, mm, ta, ls, dh)

    id.make_list(use_log=True, db_reconnect=3600 * 6, gfl_filter={"category": {"$in" ["Entrepreneur", "Public figure", "Product/service", "retail company", "Local business"]}})

