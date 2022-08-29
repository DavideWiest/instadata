import json
from modules.datahandler import DataHandler

dh = DataHandler()

with open("testdata.json", "r", encoding="utf-8") as f2:
    f = json.load(f2)

dh.restruture_data(f)

with open("testdata2.json", "w", encoding="utf-8") as f2:
    json.dump(f, f2, indent=4)
