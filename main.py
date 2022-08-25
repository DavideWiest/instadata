from instascraper import InstaScraper

USERNAME = "davidewiest"
PASSWORD = "Novigrad70"
STARTUSER = "cinephonics_alzey"

ID_FILENAME = "userids2.csv"
DATA_FILENAME = "data.json"

USERMAX = 500
LAYERMAX = 7
SLEEP_TIME = 0.5

ins = InstaScraper(USERNAME, PASSWORD, STARTUSER, LAYERMAX, USERMAX, SLEEP_TIME)
result = ins.make_list(use_file_too=True)
print(result)