from playwright.async_api import BrowserContext, PlaywrightContextManager
# from enum import Enum

type Context = BrowserContext
"""The Browser Context"""

type Playwright = PlaywrightContextManager
"""The Playwright Context Manager"""

# class State(Enum):
#     GOOD = 'good: proceed normally'
#     BAD_LOAD = 'bad: page loaded incorrectly'
#     LOGIN = 'needs login'

type GradeData = list[list[str]]
"""the grade data scraped from workday"""