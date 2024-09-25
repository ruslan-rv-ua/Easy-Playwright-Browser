from easy_playwright_browser import BrowserType
from easy_playwright_browser.sync_playwright import EasyPlaywright

browser_type = BrowserType.FIREFOX
headless = False


with EasyPlaywright(browser_type=browser_type, headless=headless) as easy_playwright:
    browser = easy_playwright.browser
    print(browser)
    page = browser.new_page()
    print(f"{page=}")
    page.goto("https://playwright.dev")
    print(page.title())
    input("Press Enter to exit...")
