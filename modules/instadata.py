from instagrapi import Client
import time
from modules.clientgetter import get_client
from geopy.geocoders import Nominatim
from datetime import datetime
import langid



class InstaData:
    def __init__(self, username, password, startuser, layermax, usermax, sleep_time, mm, ta, ls, dh):
        self.USERNAME = username
        self.PASSWORD = password
        self.STARTUSER = startuser
        self.LAYERMAX = layermax
        self.USERMAX = usermax
        self.SLEEP_TIME = sleep_time

        self.mm = mm
        self.ta = ta
        self.ls = ls
        self.dh = dh

        self.locator = Nominatim(user_agent="myGeocoder")

        self.cl = Client()
        self.cl.login(self.USERNAME, self.PASSWORD)

        self.cl2 = get_client("resources/cache.json", self.USERNAME, self.PASSWORD)

    def getaddress(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def adduser(self, id, sleep=False):
        if self.dh.check_in_db(id):
            return
        data = self.cl2.user_info(id)["user"]
        is_no_bot, botscore = self.dh.check_is_no_bot(data)
        if not is_no_bot:
            botdata = self.dh.get_botdata(data, botscore)
            self.mm.upsert_user(botdata)
            return
        elif data.get("is_memorialized", False):
            botdata = self.dh.get_memorializeddata(data)
            self.mm.upsert_user(botdata)
            return
        
        data["applicable"] = [True, "USER" if data.get("is_busines", False) == True else "BUSINESS"]
        data["populized"] = True
        data["date_last_upserted_at"] = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

        data = self.dh.delete_unneeded_fields(data)
        data = self.dh.prepare_data(data)
        data = self.dh.extract_datapoints(data)
        data = self.dh.connect_socials(data)
        data = self.dh.prepare_socialdata(data)

        textdata = ""
        data["media_latest_locations"] = {}
        data["media_hashtags"] = {}
        data["media_latest_locations_license"] = "None"

        if data["classification_level"] >= 3:
            data["media_latest_locations"], data["media_hashtags"], textdata = self.getmediadata(id)
            data["media_latest_locations_license"] = "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright"

        data["lowlevel_keywords"] = self.ta.get_keywords([(data["biography"], 5), (textdata, 2)])
        data["language"] = langid.classify(textdata + " " + data["biography"])[0]

        data = self.dh.restruture_data(data)

        self.mm.upsert_user(data)

        if sleep:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)

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

                mediahts = self.ta.gethashtags(media["caption_text"])
                for ht in mediahts:
                    if ht in hashtags:
                        hashtags[ht] += 1
                    else:
                        hashtags[ht] = 1
                
                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME / 5)
            except TypeError:
                pass
            except Exception as e:
                print(f"Error in mediadata: " + str(e))

        return locations, hashtags, textdata

    def expandreach(self, userid, layer):
        print(self.cl.user_info(userid).dict()["is_private"])
        subfollowers = self.cl.user_followers(userid, amount=100)
        print("subfollowers")
        print(list(subfollowers))
        subfollowersdict = {}
        for id in subfollowers:
            subfollowersdict[id] = layer+1

        return subfollowersdict

    def make_list(self, print_info=True, use_file_too=False):
        startuser_id = self.cl.user_id_from_username(self.STARTUSER)
        followers = self.cl.user_followers(startuser_id)
        totaluserlist = {}
        layer = 1

        for follower in list(followers)[:15]:
            totaluserlist[follower] = 1

        if use_file_too:
            with open("ids.txt", "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join([f"{k},{v}" for k, v in totaluserlist.items()]))

        breakwhile = False
        while len(totaluserlist) < self.USERMAX and layer < self.LAYERMAX:
            lastlayerlist = [k for k, v in totaluserlist.items() if v == layer]

            for followerid in lastlayerlist:
                print(2.6)
                new_user_ids = self.expandreach(followerid, layer)
                print(new_user_ids)
                totaluserlist = {**new_user_ids, **totaluserlist}

                if new_user_ids != {}:
                    for userid in new_user_ids:
                        self.adduser(userid)

                if use_file_too:
                    if new_user_ids != {}:
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
        unpop_ids = self.mm.get_all_unpopulized()

        for id in unpop_ids:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)
            self.adduser(id)

    def populize_all_from_file(self, filename="ids.txt", print_info=True):
        with open(filename, "a", encoding="utf-8") as f:
            unpop_ids = f.read().split("\n")

        unpop_ids = [int(a.split(",")[0]) for a in unpop_ids if a != ""]

        for id in unpop_ids:
            self.adduser(id)

            if print_info:
                print(f"User with the id {id} added to DB. [{unpop_ids.index(id)+1}/{len(unpop_ids)}]")
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)



