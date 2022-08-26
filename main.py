from modules.instadata import InstaData

USERNAME = "davidewiest"
PASSWORD = "Novigrad70"
STARTUSER = "mxr1tz.06" #"cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 5000
LAYERMAX = 7
SLEEP_TIME = 0.5

id = InstaData(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
print(id.getaddress(33.7878, 44.3914))
# result = id.make_list(use_file_too=True)
