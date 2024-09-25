from playwright.sync_api import sync_playwright

from . import _EasyPlaywrightBase


class EasyPlaywright(_EasyPlaywrightBase):
    def start(self) -> None:
        self._check_before_start()
        self._playwright = sync_playwright().start()
        engine = getattr(self._playwright, self.browser_name)
        executable_path = self._find_executable()
        try:
            self._browser = engine.launch_persistent_context(
                user_data_dir=self._browser_data_dir,
                headless=self.headless,
                executable_path=executable_path,
            )
        except Exception as e:
            self._playwright.stop()
            raise RuntimeError(f"Failed to start browser: {e}")

    def stop(self) -> None:
        self._check_before_stop()
        self._playwright.stop()
        self._playwright = None
        del self._browser

    def __enter__(self) -> "_EasyPlaywrightBase":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
