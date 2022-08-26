import json

with open("resources/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(len(data))

infolist = [data[a]["external_url"] for a in data if data[a]["external_url"] != None]

for a in data:
    if data[a]["emails"] != []:
        infolist.append(data[a]["emails"][0])
        print("MAIL " + data[a]["emails"][0])

for a in data:
    if data[a]["links"] != []:
        infolist.append(data[a]["links"][0])

for a in data:
    if data[a]["domains"] != []:
        infolist.append(data[a]["domains"][0])

print(len(infolist))
# for a in infolist:
#     print(a)