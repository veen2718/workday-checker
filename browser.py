import time

from playwright.async_api import async_playwright, Browser, Page, BrowserContext 
import asyncio
from bs4 import BeautifulSoup
import json
from typing import Optional

from tableParse import *
from credentials import WD_USER, WD_PW, SESSION_NAME
from wd_types import Context, Playwright, GradeData


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
    await page.fill("input[type=text]",WD_USER)
    await page.fill("input[type=password]",WD_PW)
    await page.click("button:has-text('Login')")

    await page.wait_for_url("**/home.htmld", timeout=60_000)

    await context.storage_state(path="state.json")
    print(f"successfully logged into CWL account {WD_USER}")
    

async def clear_cookies(context=None): # function I added just to easily clear cookies for testing Logins; Not currently being used
    if context is None:
        context = await browser.new_context(storage_state="state.json")
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


async def get_browser(do_head: bool, playwright: PlaywrightContextManager) -> Browser:
    """
    launches the browser
    """
    browser = await playwright.chromium.launch(
        headless=do_head,
        channel="chrome"
    )
    return browser

async def load_cookies(browser: Browser, playwright: PlaywrightContextManager) -> [Page, BrowserContext]:
    """
    loads the cookies
    """
    with open("state.json","r") as f:
        oldState = json.load(f)
    if oldState:
        context = await browser.new_context(storage_state="state.json")
    else:
        context = await browser.new_context()
    page = await context.new_page()
    return page, context
    

async def initialize_workday(page: Page, context: Context, browser: Browser) -> None:
    """
    starts up workday
    logs in if necessary
    """
    #Open page figure out if login is needed, if so login
    #await page.goto("https://wd10.myworkday.com/ubc/d/home.htmld")
    await page.goto("https://myworkday.ubc.ca")
    await page.wait_for_load_state("domcontentloaded")

    pw_locator = page.locator("input[type=password]")
    #studentButton = page.locator("Student")
    stu_btn_locator = page.get_by_role("button", name="Student")
    text_locator = page.get_by_text("There was an error loading this page, but you can still use the menu and search bar to find what you need.")


    pw_task = asyncio.create_task(
        pw_locator.wait_for(state="visible")
    )
    stu_task = asyncio.create_task(
        stu_btn_locator.wait_for(state="visible")
    )
    text_task = asyncio.create_task(
        text_locator.wait_for(state="visible")
    )

    done, pending = await asyncio.wait(
        {pw_task, stu_task, text_task},
        return_when=asyncio.FIRST_COMPLETED,
        timeout=8_000
    )

    for task in pending:
        task.cancel()
    
    if pw_task in done:
        needsLogin = True
    elif stu_task in done:
        needsLogin = False
        print("'Student' button detected - already logged in")
        time.sleep(0.2)
        
    elif text_task in done:
        return None
    #     return State.BAD_LOAD
    #     time.sleep(500)
    #     await browser.close()
    #     clear_cookies()
    #     quit()

    if needsLogin:
        await loginTo(page, context)
    
    # return State.GOOD
    return None



async def bad_page_loading(page: Page):
    """
    I started this function to fix a bug, its not finished
    but then the bug disappeared before I finished it?

    idk, workday is weird, this function isn't being used but I'm leaving it here just incase I need it later
    other functions also have code that was meant for that bug, but it doesn't seem to cause any issues
    """
    await page.get_by_role("button", name="Profile").click()
    time.sleep(0.2)
    
    # Click View Profile
    await page.locator('[data-automation-id="hammy_profile_link"]').click()


async def load_grade_page(page: Page):
    """
    loads the grade page 
    ASSUMES workday has been initialized
    """

    # navigating to academics page
    stu_btn_locator = page.get_by_role("button", name="Student")
    await stu_btn_locator.wait_for(state="visible")
    await stu_btn_locator.hover()

    academics_button = page.locator("text=Academics")
    await academics_button.wait_for(state="visible")
    await academics_button.click()
    print("clicked academics")


    # opening grades page
    await page.get_by_role("link", name="View My Grades").click()
    print("clicked 'View my Grades'")

    popup = page.locator(".wd-popup")
    await popup.wait_for(state="attached")
    textbox = popup.get_by_role("textbox").nth(1)
    await textbox.wait_for(state="visible")
    await textbox.click()


    option = page.get_by_role("option",name=SESSION_NAME) # selecting session
    await option.wait_for(state="visible")
    await option.click()

    ok_button = page.get_by_role("button", name="OK")
    await ok_button.wait_for(state="visible")
    await page.wait_for_timeout(300)
    await ok_button.click()
    print(f"selected session {SESSION_NAME}")



async def scrape_table(page: Page) -> list[list[str]]:
    """
    scrapes the grade table
    """

    table = page.get_by_role("table")
    await table.first.wait_for(state="visible")
    headers = table.locator("thead tr th")
    header_count = await headers.count()

    print(f"grade table detected")
    col_names = []
    for i in range(header_count):
        text = await headers.nth(i).inner_text()
        col_names.append(text.strip())

    rows = table.locator("tbody tr")
    row_count = await rows.count()

    all_rows = []
    for i in range(row_count):
        full_row = rows.nth(i).locator("td")
        row_col_count = await full_row.count()
        temp_row = []
        for j in range(row_col_count):
            temp_row.append(await full_row.nth(j).inner_text())
        all_rows.append(temp_row)
    
    return all_rows

def save_grade_data(old_grade_data:GradeData, all_rows: GradeData) -> str:
    """
    saves the new grade data
    and returns the notification message
    """
    parsed_grade_data = parse_grade_table(all_rows, old_grade_data)
    print(f"{parsed_grade_data.get('gradedCount')} courses already graded:")
    [print(f" - {i}") for i in parsed_grade_data.get("gradedCourses")]
    

    nf_msg = ""        
    if old_grade_data:
        if old_grade_data != all_rows:
            save_gd_to_file(all_rows, old_grade_data)
            
            print(f"Changes Detected!")
            changed_courses= parsed_grade_data.get("changedCourses")
            print(f"{parsed_grade_data.get('changedCount')} NEW course graded:")
            [print(f" - {i}") for i in changed_courses]

            nf_msg = [f"{changed_courses[0]}",f"Grade updated on workday - {parsed_grade_data.get('newGrades')[0]}!"]
        else:
            print("\nno changes :(")

    else:
        save_gd_to_file(all_rows, old_grade_data)
        print("Data has now been saved; Now the next time the script is run, it can check the new data against the previous data for changes")


def save_gd_to_file(all_rows: GradeData, old_grade_data: GradeData) -> None:
    """
    saves the grade data to json files
    """
    with open("pastOldGradeData.json","w") as f:
        json.dump(old_grade_data,f,indent=4)
    with open("gradeData.json","w") as f:
        json.dump(all_rows,f,indent=4)

async def check_workday(do_head: bool) -> None:
    """
    main function
    """
    async with async_playwright() as playwright:        
        browser = await get_browser(do_head,playwright)
        page, context = await load_cookies(browser, playwright)

        state = await initialize_workday(page, context, browser)
        # if state == State.BAD_LOAD:
        #     await bad_page_loading(page)
        
        await load_grade_page(page)
        all_rows = await scrape_table(page)

        with open("gradeData.json","r") as f:
            old_grade_data = json.load(f)

        nf_msg = save_grade_data(old_grade_data, all_rows)
        await end(browser, context)

        return nf_msg

