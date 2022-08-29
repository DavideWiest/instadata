from modules.instadata import InstaData

USERNAME = "seauser565"
PASSWORD = "Novigrad60"
STARTUSER = "cinephonics_alzey"

USERMAX = 40
LAYERMAX = 3
SLEEP_TIME = 6

MAIL_USERNAME = "webapp64@outlook.com"
MAIL_PASSWORD = "Novigrad50"

# mh = MailHandler(MAIL_USERNAME, MAIL_PASSWORD)

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
id.adduser(27551593449)
# id.adduser(1207220012)
# result = id.make_list(use_file_too=True)
