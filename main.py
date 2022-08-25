from instadata import InstaData

USERNAME = "davidewiest"
PASSWORD = "Novigrad70"
STARTUSER = "mxr1tz.06" #"cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 1000
LAYERMAX = 7
SLEEP_TIME = 0.5

ins = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
result = ins.make_list(use_file_too=True)
