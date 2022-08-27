import poplib
import time
import requests


class MailHandler():
    def __init__(self, username, password):
        self.pop3server = 'pop.gmail.com'
        self.pop3server = poplib.POP3_SSL(self.pop3server)
        self.pop3server.user(username)
        self.pop3server.pass_(password)

    def read_last_mail(self):
        for message in self.pop3server.retr(1):
            print(message)
            print(message[1])

    def extract_verification_code(self, email_body):
        email_body = email_body.split("<>")
        code = ""
        for char in email_body[1]:
            if char.isnumeric():
                code.append(char)
            else:
                break
            
        code = int(code)
        
        return code

    def quitcon(self):
        self.pop3server.quit()

    def getcode(self):
        time.sleep(20)
        code = self.extract_verification_code()
        self.quitcon()
        print(str(code) + "\n")


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
