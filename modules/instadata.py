from instagrapi import Client
import time
from modules.textanalyser import TextAnalyser
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler
from modules.clientgetter import get_client
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
import langid

mm = MongoManager()
ta = TextAnalyser()
ls = LinktreeScraper()
dh = DataHandler(mm, ta, ls)

class InstaData:
    def __init__(self, username, password, startuser, layermax, usermax, sleep_time):
        self.USERNAME = username
        self.PASSWORD = password
        self.STARTUSER = startuser
        self.LAYERMAX = layermax
        self.USERMAX = usermax
        self.SLEEP_TIME = sleep_time

        self.locator = Nominatim(user_agent="myGeocoder")

        self.cl = Client()
        self.cl.login(self.USERNAME, self.PASSWORD)

        # self.cl2 = get_client("resources/cache.json", self.USERNAME, self.PASSWORD)

    def getaddress(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def adduser(self, id):
        if dh.check_in_db(id):
            return
        if not dh.allowed_to_scrape(data):
            return

        data = self.cl2.user_info(id)
        data = dh.delete_unneeded_fields(data)
        data = dh.prepare_data(data)
        data = dh.extract_datapoints(data)
        data = dh.connect_socials(data)
        data = dh.prepare_socialdatap(data)

        textdata = ""
        data["media_latest_locations"] = {}
        data["media_hashtags"] = {}
        data["media_latest_locations_license"] = ""

        if data["classification_level"] <= 3:
            data["media_latest_locations"], data["media_hashtags"], textdata = self.getmediadata(id)
            data["media_latest_locations_license"] = "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright"

        data["lowlevel_keywords"] = ta.get_keywords([(data["biography"], 5), (textdata, 2)])
        data["language"] = langid.classify(textdata + " " + data["biography"])[0]

        data = dh.restruture_data(data)

        mm.upsert_user(data)

    def getmediadata(self, userid, number=8):
        medias = self.cl.user_medias(userid, number)
        locations = {}
        hashtags = {}
        textdata = ""
        for media in medias:
            try:
                media = media.dict()
                textdata += " " + " ".join(media["caption_text"].split(" ")[:10])
                medialoc = media["location"]
                address = self.getaddress(medialoc["lat"], medialoc["lng"])
                
                loctime = media["taken_at"].strftime("%d-%m-%Y, %H:%M:%S")
                
                if medialoc["name"] in locations:
                    locations[medialoc["name"]] = [locations[medialoc["name"]][0]+1, locations[medialoc["name"]][1]]
                else:
                    locations[medialoc["name"]] = [1, (address, medialoc["lat"], medialoc["lng"], loctime)]

                mediahts = ta.gethashtags(media["caption_text"])
                for ht in mediahts:
                    if ht in hashtags:
                        hashtags[ht] += 1
                    else:
                        hashtags[ht] = 1
                
                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME / 5)
            except Exception as e:
                print(f"Error in expandreach: " + str(e))

        return locations, hashtags, textdata

    def expandreach(self, userid, layer):
        subfollowers = self.cl.user_followers(userid, amount=100)
        subfollowersdict = {}
        for id in subfollowers:
            subfollowersdict[id] = layer+1

        return subfollowersdict

    def make_list(self, print_info=True, use_file_too=False):
        startuser_id = self.cl.user_id_from_username(self.STARTUSER)
        print(startuser_id)
        followers = self.cl.user_followers(startuser_id)
        print(followers)
        totaluserlist = {}
        layer = 1

        for follower in list(followers):
            totaluserlist[follower] = 1

        if use_file_too:
            with open("ids.txt", "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join([f"{k},{v}" for k, v in totaluserlist.items()]))

        breakwhile = False
        while len(totaluserlist) < self.USERMAX and layer < self.LAYERMAX:
            print(2.5)
            lastlayerlist = [k for k, v in totaluserlist.items() if v == layer]
            print(lastlayerlist)

            for followerid in lastlayerlist:
                print(2.6)
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

                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME)
                
            if breakwhile:
                break

            layer += 1


    def populize_all(self):
        unpop_ids = mm.get_all_unpopulized()

        for id in unpop_ids:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)
            self.adduser(id)

    def populize_all_from_file(self, filename="ids.txt"):
        with open(filename, "a", encoding="utf-8") as f:
            unpop_ids = f.read().split("\n")

        unpop_ids = [int(a.split(",")[0]) for a in unpop_ids if a != ""]

        for id in unpop_ids:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)
            self.adduser(id)



