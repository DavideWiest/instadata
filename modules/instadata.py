from instagrapi import Client
from instagrapi.exceptions import RateLimitError, PleaseWaitFewMinutes, ClientConnectionError
import time
from modules.clientgetter import get_client
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import langid
import traceback
import random
import sys
from modules.textanalyser import LocationHandler

from instagram_private_api import (ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError)
from instagrapi.exceptions import (BadPassword, ReloginAttemptExceeded, ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm, FeedbackRequired, PleaseWaitFewMinutes, LoginRequired)
from modules.custom_errors import get_full_class_name, log_account_exit, LoginFailure_cl_Primary, LoginFailure_cl_Secondary, LoginFailure_cl_Generic, LoginFailure_cl2_Secondary, LoginFailure_cl2_Generic


class Account:
    def __init__(self, username, password, proxy):
        self.username = username
        self.password = password
        self.proxy = proxy

        try:
            if proxy != "":
                self.cl = Client(proxy=proxy)
            else:
                self.cl = Client()
            self.cl.login(username, password)
            self.cl.user_info(random.choice(["41004775496", "4344434517", "49305214700"]))
        except (RateLimitError, PleaseWaitFewMinutes) as e:
            raise LoginFailure_cl_Primary(f"for user {username} - {get_full_class_name(e)}")
        except (BadPassword, ReloginAttemptExceeded, SelectContactPointRecoveryForm, RecaptchaChallengeForm, FeedbackRequired):
            raise LoginFailure_cl_Secondary(f"for user {username} - {get_full_class_name(e)}")
        except Exception as e:
            raise LoginFailure_cl_Generic(f"for user {username} - {get_full_class_name(e)}")

        try:
            self.cl2 = get_client("resources/cache.json", username, password, proxy=proxy)
        except (ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError):
            raise LoginFailure_cl2_Secondary(f"for user {username} - {get_full_class_name(e)}")
        except Exception as e:
            raise LoginFailure_cl2_Generic(f"for user {username} - {get_full_class_name(e)}")

class InstaData:
    def __init__(self, accounts_data, usermax, sleep_time, long_sleep_time, analyze_prevention, mm, ta, ls, dh, pc):
        assert len(accounts_data) > 0, "User Accounts has to have at least one user (username, password, proxy - optional)"
        
        self.accounts_data = accounts_data
        self.USERMAX = usermax
        self.SLEEP_TIME_ORIGINAL = self.SLEEP_TIME
        self.SLEEP_TIME = sleep_time / len(self.accounts_data)
        self.LONG_SLEEP_TIME = long_sleep_time
        
        self.sleep_midnights = (True, analyze_prevention[1]) if "sleep" in analyze_prevention[0].split(" ") else (False, 0)
        self.reconnect_midnights = True if "reconnect" in analyze_prevention[0].split(" ") else False

        self.mm = mm
        self.ta = ta
        self.ls = ls
        self.dh = dh
        self.pc = pc

        self.login()
        self.locator = LocationHandler()
        self.locator.set_proxies(self.proxies)
        self.locator.login()

        self.last_account = len(accounts_data)-1
    
    def login(self):
        self.proxies = list(self.pc.get_valid_proxies(max_proxies=len(self.accounts_data)))
        self.proxies = random.shuffle(self.proxies)
        self.error_account_map = {}
        
        self.accounts = []
        errorcount = 0
        for user in self.accounts_data:
            self.error_account_map[user[0]] = {"counter": 0, "errors": []}
            try:
                acc_class = Account(user[0], user[1], self.proxies[(self.accounts_data.index(user) + 1) % len(self.proxies)])
                self.accounts.append(acc_class)
            except (LoginFailure_cl_Primary, LoginFailure_cl_Secondary) as e:
                errorcount += 1
                print(e.message)
                self.add_account_error(e)
                if len(self.accounts_data) < 2:
                    print("Exiting program because the only given account failed on login")
                    sys.exit(0)

        print(f"LOGIN COMPLETED: {len(self.accounts_data) - errorcount} SUCCEEDED | {errorcount} FAILED")
        
    def cl(self):
        self.last_account += 1
        nextacc = self.accounts[(self.last_account) % len(self.accounts)]
        return nextacc.cl
    
    def cl2(self):
        self.last_account += 1
        nextacc = self.accounts[(self.last_account) % len(self.accounts)]
        return nextacc.cl2

    def get_current_account(self):
        return self.accounts[(self.last_account) % len(self.accounts)]

    def pop_account_error(self):
        crnt_acc = self.get_current_account()
        if self.error_account_map[crnt_acc.username]["counter"] > 0:
            self.error_account_map[crnt_acc.username]["counter"] -= 1
        lastitem = list(self.error_account_map[crnt_acc.username]["errors"])[-1]

        del self.error_account_map[crnt_acc.username]["errors"][lastitem]

    def add_account_error(self, e):
        crnt_acc = self.get_current_account()
        errname = get_full_class_name(e)
        errmsg = str(e)
        self.error_account_map[crnt_acc.username]["errors"].append((errname, errmsg))
        self.error_account_map[crnt_acc.username]["counter"] += 1

        if self.error_account_map[crnt_acc.username]["counter"] >= 5:
            log_account_exit(crnt_acc.username, self.error_account_map[crnt_acc.username])
            del self.accounts[self.last_account]
            self.SLEEP_TIME = self.SLEEP_TIME_ORIGINAL / len(self.accounts)
            if self.accounts_data == []:
                print("Exiting program because the only remaining account failed during scraping")
                sys.exit(0)

    def adduser(self, id):
        if self.dh.check_in_db(id):
            return
        data = self.cl2().user_info(id)["user"]
        is_no_bot, botscore = self.dh.check_is_no_bot(data)
        if is_no_bot == False:
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

    def get_mediadata(self, userid, number=8):
        medias = self.cl().user_medias(userid, number)
        locations = {}
        hashtags = {}
        textdata = ""
        for media in medias:
            try:
                media = media.dict()
                
                medialoc = media.get("location", None)
                if medialoc != None:
                    try:
                        address = self.locator.get_address(medialoc["lat"], medialoc["lng"])
                    except:
                        address = ""
                
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
            subfollowers = self.cl().user_followers(userid, amount=100)
            self.pop_account_error()
        except ClientConnectionError as e:
            print("ERROR IN expandreach: Connectionerror: skipping user")
            self.add_account_error(e)
            return {}
        subfollowersdict = {}
        for id in subfollowers:
            subfollowersdict[id] = layer+1

        return subfollowersdict
    
    def check_loop_condition(self, len_totaluserlist):
        return len_totaluserlist < self.USERMAX

    def get_first_layer(self, filter, max_amount=100):
        idlist = self.mm.pcol.aggregate([
            {"$match": filter}, 
            {"$sample": {"size": max_amount}}, 
            {"$project": {"_id": 0, "insta_id": 1}}
        ])
        
        idlist = list(idlist)
        return {a["insta_id"]: 1 for a in idlist}
        
    def make_list(self, print_info=True, use_log=False, db_reconnect=3600*6, gfl_filter={}, gfl_max_amount=200):
        totaluserlist = {}
        layer = 1

        print("SCRAPER STARTING")

        totaluserlist = self.get_first_layer(gfl_filter, gfl_max_amount)

        breakwhile = False
        while self.check_loop_condition(len(totaluserlist)):
            lastlayerlist = [k for k, v in totaluserlist.items() if v == layer]

            for followerid in lastlayerlist:
                new_user_ids = self.expandreach(followerid, layer)
                totaluserlist = {**new_user_ids, **totaluserlist}

                if new_user_ids != {}:
                    for userid in new_user_ids:
                        func_status = "UNKNOWN"
                        start = time.time()
                        try:
                            self.adduser(userid)
                            func_status = "SUCCESS"
                            self.pop_account_error()
                        except KeyboardInterrupt:
                            print("PROGRAM ENDED THROUGH C^ INPUT")
                            sys.exit(0)
                        except (PleaseWaitFewMinutes, RateLimitError) as e:
                            print("ERROR IN adduser: Program was ratelimited - retry in some hours")
                            print(traceback.format_exc())
                            func_status = "RTLMTERR"
                            self.add_account_error(e)
                        except (BadPassword, ReloginAttemptExceeded, LoginRequired, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError) as e:
                            print("ERROR IN adduser")
                            print(traceback.format_exc())
                            func_status = "INT_ERR"
                            self.add_account_error(e)
                        except ChallengeRequired as e:
                            print("ERROR IN adduser: Challenge required.")
                            print(traceback.format_exc())
                            func_status = "CLG_ERR"
                            self.add_account_error(e)
                        except Exception as e:
                            print("ERROR IN adduser")
                            print(traceback.format_exc())
                            func_status = "INT_ERR"
                            self.add_account_error(e)
                        
                        end = time.time()

                        if use_log:
                            with open("log.csv", "a", encoding="utf-8") as f:
                                f.write("\n" + func_status + "," + str(userid) + "," + str(new_user_ids[userid]) + "," + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + f"{end-start+self.SLEEP_TIME:.2f}s {end-start:.2f}s")

                        if db_reconnect not in (0, False):
                            if datetime.now() < (self.mm.last_connection_time + timedelta(seconds=db_reconnect)):
                                self.mm.connect()

                        if self.SLEEP_TIME != 0:
                            time.sleep(self.SLEEP_TIME)

                        slept_once = False
                        if self.sleep_midnights[0]:
                            dt_now = datetime.now()
                            if dt_now.hour == 23 and dt_now.minute >= 55:
                                print("---------------------")
                                print(f"GOING INTO MIDNIGHT SLEEP MODE FOR " + time.strftime('%Hh %Mm %Ss', time.gmtime(self.sleep_midnights[1])) + datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
                                print("---------------------")
                                with open("log.csv", "a", encoding="utf-8") as f:
                                    f.write("\n" + "MIDNIGHT_SLEEP_MODE" + "," + "," +  "," + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + time.strftime('%Hh %Mm %Ss', time.gmtime(self.sleep_midnights[1])))
                                
                                time.sleep(sleep_time)
                                slept_once = True
                                if self.reconnect_midnights:
                                    self.login()
                        
                        if self.LONG_SLEEP_TIME != () and not slept_once:
                            if random.randrange(1750) == 69:
                                sleep_time = random.randrange(self.LONG_SLEEP_TIME[0], self.LONG_SLEEP_TIME[1])
                                print("---------------------")
                                print(f"GOING INTO LONG SLEEP MODE FOR " + time.strftime('%Hh %Mm %Ss', time.gmtime(sleep_time)) + datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
                                print("---------------------")
                                with open("log.csv", "a", encoding="utf-8") as f:
                                    f.write("\n" + "LONG_SLEEP_MODE" + "," + "," +  "," + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + time.strftime('%Hh %Mm %Ss', time.gmtime(sleep_time)))
                                
                                time.sleep(sleep_time)

                    
                if print_info:
                    print(f"{followerid} of layer {layer} yielded {len(new_user_ids)} new users")

                if len(totaluserlist) >= self.USERMAX:
                    breakwhile = True
                    break
                        
            if breakwhile:
                break

            print(f"ADDING SCRAPING LAYER - NEXT LAYER: {layer+1}")
            with open("log.csv", "a", encoding="utf-8") as f:
                f.write("\n" + "ADDING_LAYER:" + str(layer+1) + "," + "," +  "," + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ",")
                        

            layer += 1

    # DEPRECATED: DO NOT USE
    def populize_all(self):
        unpop_ids = self.mm.get_all_unpopulized()

        for id in unpop_ids:
            if self.SLEEP_TIME != 0:
                time.sleep(self.SLEEP_TIME)
            self.adduser(id)



