from datetime import datetime
import json

class LoginFailure_cl_Primary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl - " + message

    def __str__(self):
        return self.message
    
class LoginFailure_cl_Secondary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl - " + message
    
    def __str__(self):
        return self.message

class LoginFailure_cl_Generic(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message


class LoginFailure_cl2_Secondary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message

class LoginFailure_cl2_Generic(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message

def get_full_class_name(obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + '.' + obj.__class__.__name__

def log_account_exit(username, errdict):
    with open(f"resources/logs/account_errors/info.json", "r") as f:
        logfile = json.load(f)

    logfile[username] = errdict

    with open(f"resources/logs/account_errors/info.json", "w") as f:
        json.dump(logfile, f, indent=4)

