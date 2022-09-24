import requests

API_KEY = ""

class EmailValidator():
    def __init__(self):
        self.api_key = API_KEY

    def is_valid(self, email):
        response = requests.get("https://isitarealemail.com/api/email/validate", params = {"email": email}).json()
        if "status" in response:
            return response["status"] == "valid"
        else:
            print("---------------------\nCRITICAL ERROR: REALEMAIL API NOT WORKING. Response:\n" + str(response) + "\n---------------------")
            return True
