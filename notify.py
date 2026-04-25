
from pushbullet import Pushbullet
from credentials import API_KEY


pb = Pushbullet(API_KEY)

def sendNotification(title,content):
    if API_KEY:
        push = pb.push_note(title,content)
    else:
        print("apikey not detected")


# if __name__=="__main__":
#     sendNotification("workday","test1")