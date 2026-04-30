import json

with open("constants.json","r") as f:
    constants = json.load(f)

WD_USER = constants.get("Workday-Username")
WD_PW = constants.get("Workday-Password")
API_KEY = constants.get("Pushbullet API Key")
SESSION_NAME = constants.get("SessionName")