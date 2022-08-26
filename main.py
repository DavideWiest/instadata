from modules.instadata import InstaData
from modules.mailhandler import MailHandler
import threading, time

USERNAME = "davidewiest"
PASSWORD = "Novigrad70"
STARTUSER = "mxr1tz.06" #"cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 5000
LAYERMAX = 7
SLEEP_TIME = 0.5

MAIL_USERNAME = "webapp2048@gmail.com"
MAIL_PASSWORD = ""

def getcode():
    time.sleep(20)
    mh = MailHandler()
    mh.read_last_mail()
    mh.quitcon()
    # print("123456\n")

thread = threading.Thread(target=getcode)
thread.start()

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
result = id.make_list(use_file_too=True)
