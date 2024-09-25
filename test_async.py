import asyncio

from easy_playwright_browser import BrowserType
from easy_playwright_browser.async_playwright import EasyPlaywright

browser_type = BrowserType.FIREFOX
headless = False
install_dir = r"c:\syncthing\memos\1"
data_dir = r"c:\syncthing\memos\3"


async def main():
    async with EasyPlaywright(
        browser_type=browser_type,
        headless=headless,
        browser_installation_dir=install_dir,
        browser_data_dir=data_dir,
    ) as p:
        if not p.is_browser_installed():
            p.install_browser(with_deps=True)
        browser = p.browser
        print(browser)
        page = await browser.new_page()
        print(f"{page=}")
        await page.goto("https://playwright.dev")
        print(await page.title())
        input("Press Enter to exit...")


asyncio.run(main())
