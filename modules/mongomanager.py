import pymongo
import json
import os
from bson.json_util import dumps


os.environ["con_db_username"] = "admin"
os.environ["con_db_password"] = "yeet1234"

os.environ["backup_con_db_username"] = ""
os.environ["backup_con_db_password"] = ""

HOST = "davidewiest.com"
PORT = "27017"
DB_NAME = "instadata"

BACKUP_HOST = "localhost"
BACKUP_PORT = "27017"
BACKUP_DB_NAME = "instadata_backup"

primary_collection = backup_primary_collection = "main"

class MongoManager:
    def __init__(self, user=None, password=None, host=HOST, port=PORT, db_name=DB_NAME, backup_user=None, backup_password=None, backup_host=BACKUP_HOST, backup_port=BACKUP_PORT, backup_db_name=BACKUP_DB_NAME):
        user = os.environ.get("con_db_username") if user == None else user
        password = os.environ.get("con_db_password") if password == None else password
        uri = f"mongodb://{user}:{password}@{host}:{port}"
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

        if backup_host == "localhost":
            backup_uri = f"mongodb://{backup_host}:{backup_port}"
            self.backup_client = pymongo.MongoClient(backup_uri)
            self.backup_db = self.client[backup_db_name]
        else:
            backup_user = os.environ.get("con_db_username") if backup_user == None else user
            backup_password = os.environ.get("con_db_password") if backup_password == None else password
            backup_uri = f"mongodb://{backup_user}:{backup_password}@{backup_host}:{backup_port}"
            self.backup_client = pymongo.MongoClient(backup_uri)
            self.backup_db = self.client[backup_db_name]

        self.pcol = self.db[primary_collection]
        self.bcol = self.backup_db[backup_primary_collection]
        
    def upsert_user(self, data):
        self.pcol.update_one(filter={"insta_id": data["insta_id"]}, update={"$set": data}, upsert=True)
        self.bcol.update_one(filter={"insta_id": data["insta_id"]}, update={"$set": data}, upsert=True)

    def insert_empthy_user(self, id):
        if list(self.pcol.find({"insta_id": id})) == []:
            self.pcol.insert_one({"insta_id": id})
        
        if list(self.bcol.find({"insta_id": id})) == []:
            self.bcol.insert_one({"insta_id": id})

    def get_all_unpopulized(self):
        unpop_docs = list(self.pcol.find({"populized": False}, {"_id": False, "insta_id": True, "applicable": True}))
        return [doc["insta_id"] for doc in unpop_docs]

    def export_to_json(self, filename):
        cursor = self.pcol.find({})
        with open(f"{filename}.json", "w") as file:
            json.dump(json.loads(dumps(cursor)), file)

    def is_in_db(self, id):
        return self.pcol.find_one({"insta_id": id}, {"_id": False, "insta_id": True, "date_last_upserted_at": True, "populized": True})
    
