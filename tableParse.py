import json
from datetime import datetime

from wd_types import GradeData


def parse_grade_table(all_rows: GradeData, old_rows: GradeData) -> dict:

    graded_count = 0
    graded_courses = []
    changed_count = 0
    changed_courses = []
    new_grades = []

    for i,tr in enumerate(all_rows):
        letterGrade = tr[3]
        percentageGrade = tr[4]

        # if there is a value in the letter or % grade
        if letterGrade or percentageGrade:
            if old_rows: 
                old_row = old_rows[i]

                # if the same value in previous data was blank
                if not (old_row[3] or old_row[4]):
                    changed_count += 1
                    changed_courses.append(old_row[0])
                    new_grades.append(f"{tr[3]} {tr[4]}")

                # if the grade change has already been recorded; i.e. not a new change
                else:
                    graded_count += 1
                    graded_courses.append(tr[0])
            else:
                print("no previous data saved")
                graded_count += 1
                graded_courses.append(tr[0])
    
    return {
        "gradedCount":graded_count,
        "changedCount":changed_count,
        "gradedCourses":graded_courses,
        "changedCourses":changed_courses,
        "newGrades":new_grades,
    }


def log(msg: list|str) -> None:
    """
    logs msg
    """

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

def time_fmt(t: str) -> str:
    """
    reformats t into HH:MM mm-dd
    """
    return datetime.fromisoformat(t).strftime("%H:%M %m-%d")

def last(n=10):
    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecent = logs[:n]
    logsOld = logs[n:]

    logsRecentNone = [l for l in logsRecent if l.get("message") == "no new grades"]
    logsOldChanges = [l for l in logsOld if l.get("message") != "no new grades"]

    
    if logsRecent != logsRecentNone:
        display_last_with_changes(n)
    else:
        display_last_with_no_changes(n)


def display_last_with_changes(n: int = 5) -> None:
    """
    displayes the last logs; assumes there has been a change
    """

    with open("logs.json","r") as f:
        logs = json.load(f)

    logsRecent = logs[:n]
    logsOld = logs[n:]

    logsRecentNone = [l for l in logsRecent if l.get("message") == "no new grades"]
    logsOldChanges = [l for l in logsOld if l.get("message") != "no new grades"]

    logsRecentChanges =[l for l in logsRecent if l.get("message") != "no new grades"]

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

    logsOldChanges = [l for l in logsOld if l.get("message") != "no new grades"]

    print("last checks")
    display_logs(logsRecentNone)
    
    print("\nolder changes")
    display_logs(logsOldChanges)
    


def display_log(log_data: dict) -> str:
    """
    returns the str for the given log
    """
    dt_str = time_fmt(log_data.get('time'))
    msg = log_data.get('message')
    return f"{dt_str}: {msg}"


def display_logs(log_data_list: list[dict], front: str = " - ") -> None:
    """
    displays each log in log_data_list
    adding the value of front to each log
    """
    for log_data in log_data_list:
        print(f" - {display_log(log_data)}")
