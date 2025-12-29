import json

# creating json files to store site data and grade data

for file in ["gradeData.json","logs.json","constants.json"]:
    with open(file,"w") as f:
        json.dump([],f)


with open("constants.json","w") as f:
    json.dump({
        "Workday-Username":"<YOUR-USERNAME>",
        "Workday-Password":"<YOUR-PASSWORD>",
        "Pushbullet API Key":"",
        "SessionName":"2025-26 Winter Session (UBC-V)"

    },f,indent=4)