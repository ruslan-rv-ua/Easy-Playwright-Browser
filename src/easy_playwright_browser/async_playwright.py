from playwright.async_api import async_playwright
from playwright.async_api._generated import BrowserContext

from . import _EasyPlaywrightBase


class EasyPlaywright(_EasyPlaywrightBase):
    async def start(self) -> None:
        self._check_before_start()
        self._playwright = await async_playwright().start()
        engine = getattr(self._playwright, self.browser_name)
        executable_path = self._find_executable()
        try:
            self.browser: BrowserContext = await engine.launch_persistent_context(
                user_data_dir=self._browser_data_dir,
                headless=self.headless,
                executable_path=executable_path,
            )
        except Exception as e:
            await self._playwright.stop()
            raise RuntimeError(f"Failed to start browser: {e}")

    async def stop(self) -> None:
        self._check_before_stop()
        await self._playwright.stop()
        self._playwright = None
        del self.browser

    async def __aenter__(self) -> "_EasyPlaywrightBase":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
