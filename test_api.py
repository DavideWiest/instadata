from main import STARTUSER, USERNAME, PASSWORD
from instagrapi import Client


cl = Client()
cl.login(USERNAME, PASSWORD)
result = cl.user_id_from_username(STARTUSER)
print(result)
