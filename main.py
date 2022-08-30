from modules.textanalyser import TextAnalyser
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler

from modules.instadata import InstaData
import time

USERNAME = "seauser565"
PASSWORD = "Novigrad60"
STARTUSER = "cinephonics_alzey"

USERMAX = 50
LAYERMAX = 3
SLEEP_TIME = 6

mm = MongoManager()
ta = TextAnalyser()
ls = LinktreeScraper(ta)
dh = DataHandler(mm, ta, ls)
# mh = MailHandler(MAIL_USERNAME, MAIL_PASSWORD)

start = time.time()
id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME, mm, ta, ls, dh)
end = time.time()
print(f"Logging in took {end - start:.2f} seconds")
start = time.time()
id.adduser(1207220012)
id.adduser(27551593449)
id.adduser(3121589379)

end = time.time()
print(f"Getting 3 accounts data {end - start} seconds")
print(f"Avg time: {(end - start) / 3:.2f} seconds")

start = time.time()
id.adduser(27551593449)
end = time.time()
print(f"Skipping an account took {end - start:.2f} seconds")


# id.adduser(1207220012)
# result = id.make_list(use_file_too=True)
