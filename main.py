from modules.instadata import InstaData
from modules.mailhandler import MailHandler
import threading

USERNAME = "davidewiest"
PASSWORD = "Novigrad70"
STARTUSER = "mxr1tz.06" #"cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 100
LAYERMAX = 3
SLEEP_TIME = 0

MAIL_USERNAME = "webapp2048@gmail.com"
MAIL_PASSWORD = ""

mh = MailHandler(MAIL_USERNAME, MAIL_PASSWORD)

thread = threading.Thread(target=mh.getcode)
thread.start()

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
result = id.make_list(use_file_too=True)
