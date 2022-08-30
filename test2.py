from instagram_private_api import Client
import json
import time

username = 'seauser565'
password = 'seauser656'

web_api = Client(username=username, password=password, auto_patch=True, drop_incompat_keys=False)

print(web_api.user_followers(3121589379, web_api.generate_uuid()))

# with open("resources/data.json", "r", encoding="utf-8") as f2:
#     f = json.load(f2)
#     idlist = [int(user) for user in f]

# for id in idlist[:100]:
#     userinfo = web_api.user_info(id)
#     with open("testdata2.json", "r", encoding="utf-8") as f:
#         f = json.load(f)

#     f[id] = userinfo

#     with open("testdata2.json", "w", encoding="utf-8") as f2:
#         json.dump(f, f2, indent=4)

#     time.sleep(10)
