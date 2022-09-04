from instagrapi import Client
from instagrapi.exceptions import RateLimitError, PleaseWaitFewMinutes, ClientConnectionError
import time
from modules.clientgetter import get_client
from geopy.geocoders import Nominatim
from datetime import datetime
import langid
import traceback
import random
import sys

from instagram_private_api import (ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError)
from instagrapi.exceptions import (BadPassword, ReloginAttemptExceeded, ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm, FeedbackRequired, PleaseWaitFewMinutes, LoginRequired)

class InstaData:
    def __init__(self, username, password, startuser, layermax, usermax, sleep_time, long_sleep_time, proxy, mm, ta, ls, dh):
        self.USERNAME = username
        self.PASSWORD = password
        self.STARTUSER = startuser
        self.LAYERMAX = layermax
        self.USERMAX = usermax
        self.SLEEP_TIME = sleep_time
        self.LONG_SLEEP_TIME = long_sleep_time

        self.mm = mm
        self.ta = ta
        self.ls = ls
        self.dh = dh

        self.locator = Nominatim(user_agent="myGeocoder")

        try:
            if proxy != "":
                self.cl = Client(proxy=proxy)
            else:
                self.cl = Client()
            self.cl.login(self.USERNAME, self.PASSWORD)
            self.cl.user_id_from_username(self.STARTUSER)
        except (RateLimitError, PleaseWaitFewMinutes):
            print("ERROR in self.cl.login")
            print("RATELIMITERROR: Wait a few hours before trying again")
            sys.exit(0)

        self.cl2 = get_client("resources/cache.json", self.USERNAME, self.PASSWORD, proxy=proxy)

        print("LOGIN COMPLETED")

    def get_address(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def adduser(self, id, sleep=False):
        if self.dh.check_in_db(id):
            return
        data = self.cl2.user_info(id)["user"]
        is_no_bot, botscore = self.dh.check_is_no_bot(data)
        if not is_no_bot:
            botdata = self.dh.get_botdata(data)
            self.mm.upsert_user(botdata)
            return
        elif data.get("is_memorialized", False):
            botdata = self.dh.get_memorializeddata(data)
            self.mm.upsert_user(botdata)
            return
        
        data["applicable"] = [True] + ["USER" if data.get("is_business", False) == False else "BUSINESS"]
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
        data["media_latest_locations_license"] = None

        if data["classification_level"] >= 3:
            data["media_latest_locations"], data["media_hashtags"], textdata = self.get_mediadata(id)
            data["media_latest_locations_license"] = "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright"

        data["lowlevel_keywords"] = self.ta.get_keywords([(data["biography"], 5), (textdata, 2)])
        data["language"] = langid.classify(textdata + " " + data["biography"])[0]

        data = self.dh.restruture_data(data)
        self.mm.upsert_user(data)

        if self.SLEEP_TIME != 0:
            time.sleep(self.SLEEP_TIME)
                
        if self.LONG_SLEEP_TIME != ():
            if random.randrange(1750) == 69:
                sleep_time = random.randrange(self.LONG_SLEEP_TIME[0], self.LONG_SLEEP_TIME[1])
                print("---------------------")
                print(f"GOING INTO LONG SLEEP MODE FOR {sleep_time}s ({sleep_time/60:.2f}m / {sleep_time/3600:.2f}h)")
                print("---------------------")
                time.sleep(sleep_time)


    def get_mediadata(self, userid, number=8):
        medias = self.cl.user_medias(userid, number)
        locations = {}
        hashtags = {}
        textdata = ""
        for media in medias:
            try:
                media = media.dict()
                
                medialoc = media.get("location", None)
                if medialoc != None:
                    address = self.get_address(medialoc["lat"], medialoc["lng"])
                
                    loctime = media["taken_at"].strftime("%d-%m-%Y, %H:%M:%S")
                    
                    if medialoc["name"] in locations:
                        locations[medialoc["name"]] = [locations[medialoc["name"]][0]+1, (locations[medialoc["name"]][1][0], locations[medialoc["name"]][1][1], locations[medialoc["name"]][1][2].append(loctime))]
                    else:
                        locations[medialoc["name"]] = [1, (address, medialoc["lat"], medialoc["lng"], [loctime])]

                if "caption_text" in media and media.get("caption_text") not in ("", None):
                    textdata += " " + " ".join(media["caption_text"].split(" ")[:10])
                    mediahts = self.ta.get_hashtags(media["caption_text"])
                    for ht in mediahts:
                        if ht in hashtags:
                            hashtags[ht] += 1
                        else:
                            hashtags[ht] = 1
                
                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME / 4)
            except TypeError:
                print("TYPEERROR IN get_mediadata")
                print(traceback.format_exc())
            except Exception:
                print(f"ERROR IN get_mediadata")
                print(traceback.format_exc())

        return locations, hashtags, textdata

    def expandreach(self, userid, layer):
        try:
            subfollowers = self.cl.user_followers(userid, amount=100)
        except ClientConnectionError:
            print("ERROR IN expandreach: Connectionerror: skipping user")
            return {}
        subfollowersdict = {}
        for id in subfollowers:
            subfollowersdict[id] = layer+1

        return subfollowersdict

    def make_list(self, print_info=True, use_file_too=False, startuser_amount=200):
        try:
            startuser_id = self.cl.user_id_from_username(self.STARTUSER)
            followers = self.cl.user_followers(startuser_id, amount=startuser_amount)
        except ClientConnectionError:
            print("ERROR IN make_list: Connectionerror: please restart the program")
            sys.exit(0)
        totaluserlist = {}
        layer = 1

        print("SCRAPER STARTING")

        for follower in list(followers):
            totaluserlist[follower] = 1


        breakwhile = False
        while len(totaluserlist) < self.USERMAX and layer < self.LAYERMAX:
            lastlayerlist = [k for k, v in totaluserlist.items() if v == layer]

            for followerid in lastlayerlist:
                new_user_ids = self.expandreach(followerid, layer)
                totaluserlist = {**new_user_ids, **totaluserlist}

                if new_user_ids != {}:
                    for userid in new_user_ids:
                        func_status = "UNKNOWN"
                        try:
                            self.adduser(userid)
                            func_status = "SUCCESS"
                        except KeyboardInterrupt:
                            print("PROGRAM ENDED THROUGH C^ INPUT")
                            sys.exit(0)
                        except (PleaseWaitFewMinutes, RateLimitError):
                            print("ERROR IN adduser: Program was ratelimited - retry in some hours")
                            print(traceback.format_exc())
                            func_status = "RTLMTERR"
                        except (BadPassword, ReloginAttemptExceeded, LoginRequired, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError):
                            print("ERROR IN adduser")
                            print(traceback.format_exc())
                            func_status = "INT_ERR"
                    
                        if use_file_too:
                            with open("ids.csv", "a", encoding="utf-8") as f:
                                f.write("\n" + func_status + "," + str(userid) + "," + str(new_user_ids[userid]) + "," + datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))

                if print_info:
                    print(f"{followerid} of layer {layer} yielded {len(new_user_ids)} new users")

                if len(totaluserlist) >= self.USERMAX or layer >= self.LAYERMAX:
                    breakwhile = True
                    break

                if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME)
                
                if self.LONG_SLEEP_TIME != ():
                    if random.randrange(1750) == 69:
                        sleep_time = random.randrange(self.LONG_SLEEP_TIME[0], self.LONG_SLEEP_TIME[1])
                        print("---------------------")
                        print(f"GOING INTO LONG SLEEP MODE FOR {sleep_time}s ({sleep_time/60:.2f}m / {sleep_time/3600:.2f}h)")
                        print("---------------------")
                        time.sleep(sleep_time)
            
                
            if breakwhile:
                break

            print(f"ADDING SCRAPING LAYER - NEXT LAYER: {layer+1}")

            layer += 1


    def populize_all(self):
        unpop_ids = self.mm.get_all_unpopulized()

        for id in unpop_ids:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)
            self.adduser(id)

    def populize_all_from_file(self, filename="ids.csv", print_info=True):
        with open(filename, "a", encoding="utf-8") as f:
            unpop_ids = f.read().split("\n")

        unpop_ids = [int(a.split(",")[0]) for a in unpop_ids if a != ""]

        for id in unpop_ids:
            self.adduser(id)

            if print_info:
                print(f"User with the id {id} added to DB. [{unpop_ids.index(id)+1}/{len(unpop_ids)}]")
            
            if self.SLEEP_TIME != 0:
                    time.sleep(self.SLEEP_TIME)
                
            if self.LONG_SLEEP_TIME != ():
                if random.randrange(1750) == 69:
                    sleep_time = random.randrange(self.LONG_SLEEP_TIME[0], self.LONG_SLEEP_TIME[1])
                    print("---------------------")
                    print(f"GOING INTO LONG SLEEP MODE FOR {sleep_time}s ({sleep_time/60:.2f}m / {sleep_time/3600:.2f}h)")
                    print("---------------------")
                    time.sleep(sleep_time)
            


