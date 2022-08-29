import requests


class EmailValidator():
    def __init__(self):
        self.api_key = "96124839-5566-47b0-a943-d8299839bd62"

    def is_valid(self, email):
        response = requests.get("https://isitarealemail.com/api/email/validate", params = {'email': email})
        response = response.json()
        if "status" in response:
            return response['status'] == "valid"
        
        print("---------------------")
        print("CRITICAL ERROR: REALEMAIL API NOT WORKING. Response:")
        print(response)
        print("---------------------")
        return True
