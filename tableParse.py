import json
from datetime import datetime


def parseGradeTable(t,t0):
    gradedCount = 0
    gradedCourses = []
    changedCount = 0
    changedCourses = []
    newGrades = []
    for i,tr in enumerate(t):
        letterGrade = tr[3]
        percentageGrade = tr[4]
        if letterGrade or percentageGrade:
            if t0: 
                trOld = t0[i]
                if not (trOld[3] or trOld[4]):
                    changedCount += 1
                    changedCourses.append(trOld[0])
                    newGrades.append(f"{tr[3]} {tr[4]}")
                else:
                    gradedCount += 1
                    gradedCourses.append(tr[0])
            else:
                print("no previous data saved")
                gradedCount += 1
                gradedCourses.append(tr[0])
    
    return {
        "gradedCount":gradedCount,
        "changedCount":changedCount,
        "gradedCourses":gradedCourses,
        "changedCourses":changedCourses,
        "newGrades":newGrades,
    }


def log(msg):
    with open("logs.json","r") as f:
        logs = json.load(f)
    
    if type(msg) == list:
        msg = " ".join(msg)
    logs.insert(0,{
        "time":datetime.now().isoformat(),
        "message": msg
    })
    with open("logs.json","w") as f:
        json.dump(logs,f,indent=4)


def last(n=5):
    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecent = logs[:n]
    logsOld = logs[n:]

    logsRecentNone = [l for l in logsRecent if l.get("message") == "no new changes"]
    logsOldChanges = [l for l in logsOld if l.get("message") != "no new changes"]

    def timeFmt(t):
        return datetime.fromisoformat(t).strftime("%H:%M %m-%d")
    
    if logsRecent == logsRecentNone:
        print("No recent changes. Last Checks:")
        for l in logsRecent:
            print(f" - {timeFmt(l.get('time'))}")
        print("\nLast Changes at:")
    else:
        print("RECENT CHANGE:")
        for l in [l0 for l0 in logsRecent if l0 not in logsRecentNone]:
            print(f"'{l.get("message")}' at {timeFmt(l.get('time'))}")
        print("\nOlder Changes:")

    for l in logsOldChanges:
        print(f"'{l.get('message')}' at {timeFmt(l.get('time'))}")
    

