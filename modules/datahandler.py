from datetime import datetime
import json
from modules.websiteanalyser import WebsiteAnalyser
from modules.mailhandler import EmailValidator

wa = WebsiteAnalyser()
ev = EmailValidator()

class DataHandler():
    def __init__(self, mm, ta, ls):
        self.mm = mm
        self.ta = ta
        self.ls = ls

        with open("resources/social_websites.txt", "r") as f:
            f = f.read().split("\n")

        self.social_network_list = f

        with open("resources/most_used_websites.txt", "r") as f:
            f = f.read().split("\n")

        self.most_used_websites = f

        with open("resources/unneeded_fields.txt", "r") as f:
            f = f.read().split("\n")

        self.unneeded_fields = f

        with open("resources/datamigration.json", "r", encoding="utf-8") as f:
            self.datamigrationdicts = json.load(f)

    def link_is_social(self, link):
        for social_link in self.social_network_list:
            if social_link in link:
                return social_link.split(".")[0]

        return False
    
    def link_is_common(self, link):
        for common_link in self.most_used_websites:
            if common_link in link:
                return common_link.split(".")[0]

        return False

    def classify_user(self, data):
        userlevel = 0
        userlevel -= 1 if data["is_private"] == False else 0
        userlevel += 1 if len(data["social_profiles"]) >= 2 else 0
        userlevel += 3 * len(data["emails"])
        userlevel += 1 * len(data["phone_numbers"])
        userlevel += 2 * len([v for k, v in data["domains"].items() if v == 1])
        userlevel += 1 * len([v for k, v in data["links"].items() if v == 1])
        return userlevel

    def delete_unneeded_fields(self, data):
        data = {k:v for k, v in data.items() if k not in self.unneeded_fields}
        return data

    def check_is_bot(self, data):
        if data["is_verified"] == True:
            print("is verified")
            return False
        botscore = 0
        botscore += 1 if (data["follower_count"] / data["following_count"] + 1) > 4 else 0
        botscore += 1 if data["follower_count"] < 20 else 0
        botscore += 1 if data["biography"] == "" else 0
        botscore += 1 if data["media_count"] < 10 else 0
        botscore += 1 if data["has_anonymous_profile_picture"] else 0
        botscore += 1 if data["is_new_to_instagram"] else 0
        print("botscore")
        print(botscore)
        return botscore >= 3
    
    def check_is_momorialized(self, is_memorialized):
        return is_memorialized

    def check_in_db(self, id):
        in_db = self.mm.is_in_db(id)
        if in_db == None:
            return False
        else:
            delta = datetime.now() - in_db["date_last_updated_at"].strptime("%d-%m-%Y, %H:%M:%S")
            return delta.days < 30

    def allowed_to_store(self, data):
        a = self.check_is_bot(data)
        b = self.check_is_momorialized(data["user"]["is_memorialized"])
        return a and b
        # return self.check_is_momorialized(data["user"]["is_memorialized"]) and self.check_is_bot(data)

    def complete_social_profile(self, data):
        data["social_media_profiles"] = {
            "instagram": "https://instagram.com/" + data["username_original"]
        }
        for link in data["link"] + [data["external_url"]]:
            if "linktr.ee" in link:
                data["social_media_profiles"]["linktree"] = self.ta.findlinks([link], rfn=True) or link
                data = self.ls.getlinktreedata(data, self.ta.findlinks([link], rfn=True) or link)
            
            for social_network in self.social_network_list:
                if social_network in link:
                    data["social_media_profiles"][social_network.split(".")[0] if social_network != "youtu.be" else "youtube"] = link

        return data

    def prepare_data(self, data):
        data["username_original"] = data["username"]
        data["full_name_original"] = data["full_name"]
        data["biography_original"] = data["biography"]

        data["username"] = self.ta.normalize_all(data["username"])
        data["full_name"] = self.ta.normalize_all(data["full_name"])
        data["biography"] = self.ta.normalize_all(data["biography"])

        data["username"] = self.ta.parse_direct_chars(data["username"])
        data["full_name"] = self.ta.parse_direct_chars(data["full_name"])
        data["biography"] = self.ta.parse_direct_chars(data["biography"])

        data["id"] = id
        data["date_last_updated_at"] = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

        return data

    def is_valuable_domain(self, url):
        return not any([domain in url for domain in self.most_used_websites])

    def extract_datapoints(self, data):
        data["gender"] = self.ta.get_gender(data["full_name"])
        data["emails"] = []
        data["phone_numbers"] = []
        data["domains"] = {}
        data["links"] = {}

        if data.get("public_email") not in ("", None):
            data["emails"].append(data["public_email"])
        data["emails"] = data["emails"] + self.ta.findemails(data["biography"])
        data["emails"] = list(dict.fromkeys(data["emails"]))

        if data.get("external_url") not in ("", None):
            if not wa._has_subroute(data["external_url"]):
                data["domains"][data["external_url"]] = 0
            else:
                data["inks"][data["external_url"]] = 0
        
        if data.get("website") not in ("", None):
            if not wa._has_subroute(data["website"]):
                data["domains"][data["website"]] = 0
            else:
                data["inks"][data["website"]] = 0

        if "biography" in data:
            for domain in self.ta.finddomains(data["biography"]):
                data["domains"][domain] = 0
            for link in self.ta.findlinks(data["biography"]):
                data["links"][link] = 0
        
        for domain in data["domains"]:
            data["domains"][domain] = 1 if self.is_valuable_domain(domain) else 0
        for link in data["links"]:
            data["links"][link] = 1 if self.is_valuable_domain(link) else 0        

        if data.get("public_phone_number") not in ("", None):
            data["phone_numbers"].append(data["public_phone_number"])
        if data.get("contact_phone_number") not in ("", None):
            data["phone_numbers"].append(data["contact_phone_number"])
        data["phone_numbers"] = list(dict.fromkeys(data["phone_numbers"]))

        account_type_dict = {
            0: "normal/consumer",
            1: "business",
            2: "creative/self-employed",
            None: ""
        }
        data["account_type"] = account_type_dict[data["account_type"]]

        data["hashtags"] = []
        data["tagged_users"] = []
        if "biography" in data:
            for entity in data["biography_with_entities"]["entities"]:
                if "user" in entity:
                    data["tagged_users"].append(entity["user"]["username"])
                elif "hashtag" in entity:
                    data["hashtags"].append(entity["hashtag"]["name"])

        return data


    def connect_socials(self, data):
        data["social_profiles"] = {}
        data["social_profiles"]["instagram"] = {"link": "https://instagram.com/" + data["username"]}
        for link in data["links"]:
            if "linktr.ee" in link:
                data["social_profiles"]["linktree"] = {"link": link}
            
            for social_link in self.social_network_list:
                if social_link in link:
                    data["social_profiles"][social_link.split(".")[0]] = {"link": link}
        
        data["classification_level"] = self.classify_user(data)

        return data

    def prepare_socialdata(self, data):

        for to_key, from_key in self.datamigrationdicts["insta_datamigrationdict"].items():
            data["social_profiles"]["instagram"][to_key] = data.get(from_key, None)
        
        for to_key, from_key in self.datamigrationdicts["insta_datastatsmigrationdict"].items():
            data["social_profiles"]["instagram"]["stats"][to_key] = data.get(from_key, None)



        if "linktree" in data["social_profiles"]:
            linktreedata = self.ls.get_linktree(data["social_profiles"]["linktree"]["link"])
            for link in linktreedata["links"]:
                data["links"].append(link)
            linktreedata["profile_picture"] = linktreedata["avatar_image"]
            a = linktreedata.pop("updated_at", None)
            a = linktreedata.pop("is_active", None)
            a = linktreedata.pop("links", None)
            a = linktreedata.pop("avatar_image", None)
            data["social_profiles"]["linktree"] = linktreedata

        return data

    def restruture_data(self, data):
        for category in self.datamigrationdicts["main_datamigration"]:
            if category not in data:
                data[category] = {}
            for to_key, from_key in self.datamigrationdicts["main_datamigration"][category]:
                data[category][to_key] = data.get(from_key, None)

        for to_key, from_key in self.datamigrationdicts["standalone_accepted_vars"]:
            data[to_key] = data.get(from_key, None)

        for key in list(data):
            if key not in list(self.datamigrationdicts["main_datamigration"]) and not key in list([a[0] for a in self.datamigrationdicts["standalone_accepted_vars"]]):
                del data[key]

        return data


