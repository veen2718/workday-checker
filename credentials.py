import json

with open("constants.json","r") as f:
    constants = json.load(f)

wdUser = constants.get("Workday-Username")
wdPw = constants.get("Workday-Password")
apikey = constants.get("Pushbullet-API-Key")
sessionName = constants.get("SessionName")