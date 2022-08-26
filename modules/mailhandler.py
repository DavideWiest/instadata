import poplib



class MailHandler():
    def __init__(self, username, password):
        self.pop3server = 'pop.gmail.com'
        self.pop3server = poplib.POP3_SSL(self.pop3server)
        self.pop3server.user(username)
        self.pop3server.pass_(password)

    def read_last_mail(self):
        for message in self.pop3server.retr(1):
            print(message)

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