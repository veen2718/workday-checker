
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
import json

from tableParse import *
from credentials import wdUser, wdPw, sessionName


async def end(browser, context):
    # input("press enter to close")
    await context.storage_state(path="state.json")
    
    with open("state.json","r") as f:
        finalState = json.load(f)
    with open("state.json","w") as f:
        json.dump(finalState,f,indent=4)
    await browser.close()


async def loginTo(page, context):
    print("commencingLogin")
    await page.fill("input[type=text]",wdUser)
    await page.fill("input[type=password]",wdPw)
    await page.click("button:has-text('Login')")

    await page.wait_for_url("**/home.htmld", timeout=60_000)

    await context.storage_state(path="state.json")
    print(f"successfully logged into CWL account {wdUser}")
    

async def cookieClear(context): # function I added just to easily clear cookies for testing Logins; Not currently being used
    cookies = await context.cookies()

    workdayCookies = [
        c for c in cookies
        if "myworkday.com" in c["domain"]
    ]

    await context.clear_cookies() 
    await context.add_cookies([
        c for c in cookies
        if c not in workdayCookies
    ])



async def checkWorkday(doHead):
    async with async_playwright() as playwright:
        
        "setup Things:"
        browser = await playwright.chromium.launch(
            headless=doHead
        )

        with open("state.json","r") as f:
            oldState = json.load(f)
        if oldState:
            context = await browser.new_context(storage_state="state.json")
        else:
            context = await browser.new_context()
        page = await context.new_page()



        #Open page figure out if login is needed, if so login
        await page.goto("https://wd10.myworkday.com/ubc/d/home.htmld")
        await page.wait_for_load_state("domcontentloaded")

        passwordLocator = page.locator("input[type=password]")
        academicsButton = page.get_by_role("button",name="Academics")

        passwordTask = asyncio.create_task(
            passwordLocator.wait_for(state="visible")
        )
        academicTask = asyncio.create_task(
            academicsButton.wait_for(state="visible")
        )

        done, pending = await asyncio.wait(
            {passwordTask, academicTask},
            return_when=asyncio.FIRST_COMPLETED,
            timeout=8
        )

        for task in pending:
            task.cancel()

        if passwordTask in done:
            needsLogin = True
        else:
            needsLogin = False
            print("'Academics' button detected - already logged in")


        if needsLogin:
            await loginTo(page, context)







        #navigating to grades
        await academicsButton.click()
        print("clicked academics")
        await page.get_by_role("link", name="View My Grades").click()
        print("clicked 'View my Grades'")

        popup = page.locator(".wd-popup")
        await popup.wait_for(state="attached")

        textbox = popup.get_by_role("textbox").nth(1)
        await textbox.wait_for(state="visible")
        await textbox.click()

        option = page.get_by_role("option",name=sessionName)
        await option.wait_for(state="visible")


        await option.click()

        okButton = page.get_by_role("button", name="OK")
        await okButton.wait_for(state="visible")
        await page.wait_for_timeout(300)
        await okButton.click()
        print(f"selected session {sessionName}")
        

        #Table Parsing stuff:
        table = page.get_by_role("table")
        await table.first.wait_for(state="visible")
        headers = table.locator("thead tr th")
        headerCount = await headers.count()
        print(f"grade table detected")
        columnNames = []
        for i in range(headerCount):
            text = await headers.nth(i).inner_text()
            columnNames.append(text.strip())
        print(columnNames)



        rows = table.locator("tbody tr")
        rowCount = await rows.count()
        print(f"rowcount {rowCount}")

        allRows = []
        for i in range(rowCount):
            fullRow = rows.nth(i).locator("td")
            rowColCount = await fullRow.count()
            tempRow = []
            for j in range(rowColCount):
                tempRow.append(await fullRow.nth(j).inner_text())
            allRows.append(tempRow)
        
        print("Data")
        [print(x) for x in allRows]

        with open("gradeData.json","r") as f:
            oldGradeData = json.load(f)
        
        print("\n\n\n\n\n\n\n\n\n\n")
        parsedGradeData = parseGradeTable(allRows, oldGradeData)
        print(f"{parsedGradeData.get('gradedCount')} courses already graded:")
        [print(f" - {i}") for i in parsedGradeData.get("gradedCourses")]
        

        nfMsg = ""        
        if oldGradeData:
            if oldGradeData != allRows:
                with open("pastOldGradeData.json","w") as f:
                    json.dump(oldGradeData,f,indent=4)
                with open("gradeData.json","w") as f:
                    json.dump(allRows,f,indent=4)
                
                print(f"Changes Detected!")
                changedCourses= parsedGradeData.get("changedCourses")
                print(f"{parsedGradeData.get('changedCount')} NEW course graded:")
                [print(f" - {i}") for i in changedCourses]

                nfMsg = [f"Grade Updated On Workday!",f"{changedCourses[0]} - {parsedGradeData.get('newGrades')[0]}!"]
            else:
                print("\nno changes :(")
        else:
            with open("pastOldGradeData.json","w") as f:
                json.dump(oldGradeData,f,indent=4)
            with open("gradeData.json","w") as f:
                json.dump(allRows,f,indent=4)
            print("Data has now been saved; Now the next time the script is run, it can check the new data against the previous data for changes")
        



        await end(browser, context)
        return nfMsg

