
from pushbullet import Pushbullet
from credentials import apikey


pb = Pushbullet(apikey)

def sendNotification(title,content):
    if apikey:
        push = pb.push_note(title,content)
    else:
        print("apikey not detected")


# if __name__=="__main__":
#     sendNotification("workday","test1")