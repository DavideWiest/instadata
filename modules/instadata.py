from instagrapi import Client
import time
from modules.textanalyser import TextAnalyser
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
import langid

ta = TextAnalyser()
mm = MongoManager()
ls = LinktreeScraper()

class InstaData:
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
        self.empthy_fields = ["account_type", "address_street", "category", "city_id", "city_name", "contact_phone_number", "instagram_location_id", "interop_messaging_user_fbid", "latitude", "longitude", "public_email", "public_phone_country_code", "public_phone_number", "zip"]

        with open("resources/social_websites.txt", "r") as f:
            f = f.read().split("\n")

        self.social_network_list = f

        with open("resources/most_used_websites.txt", "r") as f:
            f = f.read().split("\n")

        self.most_used_websites = f

    def getaddress(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def is_bot(self, data):
        # run statements with rough score
        botscore = 0
        botscore += 1 if (data["follower_count"] / data["following_count"] + 1) > 4 else 0
        botscore += 1 if data["follower_count"] < 20 else 0
        botscore += 1 if data["biography"] == "" else 0
        botscore += 1 if data["media_count"] < 10 else 0
        botscore += 1 if data["profile_pic_url"] in ("", None, "UNKNOWN") else 0
        return botscore >= 3

    def is_valuable_domain(self, url):
        return not any([domain in url for domain in self.most_used_websites])

    def upsertion_unallowed(self, id):
        in_db = mm.is_in_db(id)
        if in_db == None:
            return False
        else:
            delta = datetime.now() - in_db["date_last_updated_at"].strptime("%d-%m-%Y, %H:%M:%S")
            return delta.days < 30

    def adduser(self, id):

        if self.upsertion_unallowed(id):
            return

        userinfo = self.cl.user_info(id).dict()
        data = userinfo

        if self.is_bot(data):
            return

        for key in data:
            if key in self.empthy_fields:
                del data[key]

        username = data["username"]

        data["username"] = ta.normalize_all(userinfo["username"])
        data["full_name"] = ta.normalize_all(userinfo["full_name"])
        data["biography"] = ta.normalize_all(userinfo["biography"])

        data["username"] = " " + ta.parse_direct_chars(userinfo["username"]) + " "
        data["full_name"] = " " + ta.parse_direct_chars(userinfo["full_name"]) + " "
        data["biography"] = " " + ta.parse_direct_chars(userinfo["biography"]) + " "

        data["id"] = id
        data["date_last_updated_at"] = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
        data["gender"] = ta.get_gender(data["full_name"])
        domains = ta.finddomains(data["biography"] + " " + data["full_name"] + " " + (data["external_url"] or ""))
        links = ta.findlinks(data["biography"] + " " + data["full_name"] + " " + (data["external_url"] or ""))
        data["emails"] = ta.findemails(data["biography"] + " " + data["full_name"])

        data["domains"] = {}
        for domain in domains:
            data["domains"][domain] = 1 if self.is_valuable_domain(domain) else 0

        data["links"] = {}
        for link in links:
            data["links"][link] = 1 if self.is_valuable_domain(link) else 0

        data["social_media_profiles"] = {
            "instagram": "https://instagram.com/" + username
        }
        for link in data["link"] + [data["external_url"]]:
            if "linktr.ee" in link:
                data["social_media_profiles"]["linktree"] = ta.findlinks([link], rfn=True) or link
                data = ls.getlinktreedata(data, ta.findlinks([link], rfn=True) or link)
            
            for social_network in self.social_network_list:
                if social_network in link:
                    data["social_media_profiles"][social_network.split(".")[0] if social_network != "youtu.be" else "youtube"] = link

        textdata = ""
        if data["is_private"] == False and (data["social_media_profiles"].get("linktree", None) != None or data["emails"] != [] or any([v == 1 for k, v in data["domains"].items()])):
            data["mentioned_names"] = ta.findnames(data["biography"])
            data["latest_locations"], data["hashtags"], textdata = self.getmediadata(id)
        
        data["keywords"] = ta.get_keywords((data["biography"], 5), (textdata, 2))
        
        textdata += " " + data["biography"]

        data["language"] = langid.classify(textdata)[0]

        mm.upsert_user(data)

    def getmediadata(self, userid, number=8):
        medias = self.cl.user_medias(userid, number)
        locations = {}
        hashtags = {}
        textdata = ""
        for media in medias:
            try:
                media = media.dict()
                textdata += " " + " ".join(media["caption_text"].split(" ")[:8])
                medialoc = media["location"]
                address = self.getaddress(medialoc["lat"], medialoc["lng"])
                
                mediatime = media["taken_at"]
                loctime = mediatime.strftime("%d-%m-%Y, %H:%M:%S")
                
                if medialoc["name"] not in locations:
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
                    time.sleep(self.SLEEP_TIME / 10)
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

                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME)
                
            if breakwhile:
                break

            layer += 1

        return totaluserlist

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
