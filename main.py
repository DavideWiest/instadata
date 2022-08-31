from modules.textanalyser import TextAnalyser
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler

from modules.instadata import InstaData
import time

USERNAME = "seauser565"
PASSWORD = "seauser656"
STARTUSER = "crcr_studio" # "cinephonics_alzey"

USERMAX = 10000
LAYERMAX = 10
SLEEP_TIME = 9
LONG_SLEEP_TIME = (60 * 60 * 0.5, 60 * 60 * 1.75)

mm = MongoManager()
ta = TextAnalyser()
ls = LinktreeScraper(ta)
dh = DataHandler(mm, ta, ls)

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, mm, ta, ls, dh)

start = time.time()
id.make_list(use_file_too=True)
end = time.time()
print(f"Getting {USERMAX} accounts data took {end - start} seconds")
print(f"Average time per account: {(end - start) / USERMAX:.2f} seconds")

