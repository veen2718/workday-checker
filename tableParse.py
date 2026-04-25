import json
from datetime import datetime


def parse_grade_table(t,t0):
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

def timeFmt(t):
    return datetime.fromisoformat(t).strftime("%H:%M %m-%d")

def last(n=5):
    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecent = logs[:n]
    logsOld = logs[n:]

    logsRecentNone = [l for l in logsRecent if l.get("message") == "no new changes"]
    logsOldChanges = [l for l in logsOld if l.get("message") != "no new changes"]

    
    if logsRecent != logsRecentNone:
        display_last_with_changes(n)
    else:
        display_last_with_no_changes(n)

    #     print("RECENT CHANGE:")
    #     for l in [l0 for l0 in logsRecent if l0 not in logsRecentNone]:
    #         print(f"'{l.get("message")}' at {timeFmt(l.get('time'))}")
    #     print("\nOlder Changes:")
    # else:
    #     print("No recent changes. Last Checks:")

    # for l in logsRecent:
    #     print(f" - {timeFmt(l.get('time'))}")

    # if logsRecent == logsRecentNone:    
    #     print("\nLast Changes at:")
    

    # for l in logsOldChanges:
    #     print(f"'{l.get('message')}' at {timeFmt(l.get('time'))}")
    

def display_last_with_changes(n: int = 5) -> None:
    """
    displayes the last logs; assumes there has been a change
    """

    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecent = logs[:n]
    logsOld = logs[n:]

    logsRecentNone = [l for l in logsRecent if l.get("message") == "no new changes"]
    logsOldChanges = [l for l in logsOld if l.get("message") != "no new changes"]

    logsRecentChanges =[l for l in logsRecent if l.get("message") != "no new changes"]

    print("RECENT CHANGE")
    display_logs(logsRecentChanges)
    
    print("\nall recent checks")
    display_logs(logsRecent)

    print("\nolder changes")
    display_logs(logsOldChanges)


def display_last_with_no_changes(n: int = 5) -> None:
    """
    displayes the last logs; assumes there has been no change
    """

    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecentNone = logs[:n]
    logsOld = logs[n:]

    logsOldChanges = [l for l in logsOld if l.get("message") != "no new changes"]

    print("last checks")
    display_logs(logsRecentNone)
    
    print("\nolder changes")
    display_logs(logsOldChanges)
    


def display_log(log_data: dict) -> str:
    """
    returns the str for the given log
    """
    dt_str = timeFmt(log_data.get('time'))
    msg = log_data.get('message')
    return f"{dt_str}: {msg}"


def display_logs(log_data_list: list[dict], front: str = " - ") -> None:
    """
    displays each log in log_data_list
    adding the value of front to each log
    """
    for log_data in log_data_list:
        print(f" - {display_log(log_data)}")
