from instagrapi import Client
import time
from textanalyser import TextAnalyser
from mongomanager import MongoManager
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

ta = TextAnalyser()
mm = MongoManager()

class InstaScraper:
    def __init__(self, username, password, startuser, layermax, usermax, sleep_time):
        self.USERNAME = username
        self.PASSWORD = password
        self.STARTUSER = startuser
        self.LAYERMAX = layermax
        self.USERMAX = usermax
        self.SLEEP_TIME = sleep_time

        self.cl = Client()
        self.cl.login(self.USERNAME, self.PASSWORD)
        self.locator = Nominatim(user_agent="myGeocoder")

    def getaddress(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def adduser(self, id):

        userinfo = self.cl.user_info(id).dict()
        data = userinfo

        data["username"] = ta.normalize_all(userinfo["username"])
        data["full_name"] = ta.normalize_all(userinfo["full_name"])
        data["biography"] = ta.normalize_all(userinfo["biography"])

        data["id"] = id
        data["domains"] = ta.finddomains(data["biography"] + " " + data["full_name"])
        data["links"] = ta.findlinks(data["biography"] + " " + data["full_name"])
        data["emails"] = ta.findemails(data["biography"] + " " + data["full_name"])
        data["keywords"] = ta.findkeywords(data["biography"] + " " + data["full_name"])
        data["mentioned_names"] = ta.findnames(data["biography"])
        data["latest_locations"] = self.getlatestlocations(id)
    
        mm.upsert_user(data)

    def getlatestlocations(self, userid, number=10):
        medias = self.cl.user_medias(userid, number)
        locations = []
        for media in medias:
            try:
                media = media.dict()
                medialoc = media["location"]
                mediatime = media["taken_at"]
                loc = self.getaddress(medialoc["lat"], medialoc["lng"])
                loc["name"] = medialoc["name"]
                loc["time"] = mediatime.strftime("%d-%m-%Y, %H:%M:%S")
                locations.append(loc)
                time.sleep(self.SLEEP_TIME / 10)
            except Exception as e:
                print(f"Error in expandreach: " + str(e))

        return locations

    def expandreach(self, userid, layer):
        subfollowers = self.cl.user_followers(userid, amount=100)
        subfollowersdict = {}
        for id in subfollowers:
            subfollowersdict[id] = layer+1

        return subfollowersdict

    def make_list(self, print_info=True, use_file_too=False):
        startuser_id = self.cl.user_id_from_username(self.STARTUSER)
        followers = self.cl.user_followers(startuser_id)
        totaluserlist = {}
        layer = 1

        for follower in list(followers):
            totaluserlist[follower] = 1

        if use_file_too:
            with open("ids.txt", "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join([f"{k},{v}" for k, v in totaluserlist.items()]))

        breakwhile = False
        while len(totaluserlist) < self.USERMAX and layer < self.LAYERMAX:
            lastlayerlist = [k for k, v in totaluserlist.items() if v == layer]

            for followerid in lastlayerlist:
                new_user_ids = self.expandreach(followerid, layer)
                totaluserlist = {**new_user_ids, **totaluserlist}

                if new_user_ids != {}:
                    for userid in new_user_ids:
                        self.adduser(userid)

                if use_file_too:
                    with open("ids.txt", "a", encoding="utf-8") as f:
                        f.write("\n" + "\n".join([f"{k},{v}" for k, v in new_user_ids.items()]))

                if not (len(totaluserlist) < self.USERMAX and layer < self.LAYERMAX):
                    breakwhile = True
                    break

                if print_info:
                    print(f"{followerid} ({len(totaluserlist)}) of layer {layer} yielded {len(new_user_ids)} new users")

            if breakwhile:
                break

            layer += 1

        return totaluserlist

    def populize_all(self):
        unpop_ids = mm.get_all_unpopulized()

        for id in unpop_ids:
            time.sleep(self.SLEEP_TIME)
            self.adduser(id)

    def populize_all_from_file(self, filename="ids.txt"):
        with open(filename, "a", encoding="utf-8") as f:
            unpop_ids = f.read().split("\n")

        unpop_ids = [int(a.split(",")[0]) for a in unpop_ids if a != ""]

        for id in unpop_ids:
            time.sleep(self.SLEEP_TIME)
            self.adduser(id)
