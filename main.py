from modules.instadata import InstaData
# from modules.mailhandler import MailHandler
# import threading

USERNAME = "seauser565"
PASSWORD = "Novigrad60"
STARTUSER = "cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 40
LAYERMAX = 3
SLEEP_TIME = 6

MAIL_USERNAME = "webapp64@outlook.com"
MAIL_PASSWORD = "Novigrad50"

# mh = MailHandler(MAIL_USERNAME, MAIL_PASSWORD)

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
result = id.make_list(use_file_too=True)
