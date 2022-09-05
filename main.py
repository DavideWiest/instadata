from modules.textanalyser import TextAnalyser
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper

from modules.instadata import InstaData
import time

USERNAME = "seauser565"
PASSWORD = "seauser656"
STARTUSER = "motivationandhustle1" # "maxime.batouche" # "cinephonics_alzey"

USERMAX = float("inf") #10000
LAYERMAX = float("inf") #10
SLEEP_TIME = 8
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 1.75)

PROXY = ""

if __name__ == "__main__":
    mm = MongoManager()
    ta = TextAnalyser()
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    dh = DataHandler(mm, ta, ls)

    id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, PROXY, mm, ta, ls, dh)

    start = time.time()
    id.make_list(use_file_too=True)
    end = time.time()

    print(f"Getting {USERMAX} accounts data took {end - start} seconds")
    print(f"Average time per account: {(end - start) / USERMAX:.2f} seconds")
