from enum import Enum
from pathlib import Path
from subprocess import run

from playwright._impl._driver import (
    compute_driver_executable,  # type: ignore
    get_driver_env,
)
from playwright.sync_api import sync_playwright

BROWSER_DATA_DEFAULT_DIR = "BROWSERS_DATA"
BROWSER_DEFAULT_INSTALLATION_DIR = "INSTALLED_BROWSERS"


class BrowserType(Enum):
    CHROMIUM = 0
    FIREFOX = 1
    WEBKIT = 2


class EasyPlaywright:
    def __init__(
        self,
        browser_type: BrowserType = BrowserType.CHROMIUM,
        headless: bool = True,
        browser_data_dir: Path | str | None = None,
        browser_installation_dir: Path | str | None = None,
    ) -> None:
        self._browser_type = browser_type
        match browser_type:
            case BrowserType.CHROMIUM:
                self._browser_name = "chromium"
                self._browser_executable = "chrome-win/chrome.exe"  # TODO: os specific
            case BrowserType.FIREFOX:
                self._browser_name = "firefox"
                self._browser_executable = "firefox/firefox.exe"
            case BrowserType.WEBKIT:
                self._browser_name = "webkit"
                self._browser_executable = "Playwright.exe"
            case _:
                raise ValueError(f"Unknown browser type: {browser_type}")

        self._headless = headless

        current_dir = Path(__file__).resolve().parent
        self._browser_data_dir = (
            Path(browser_data_dir)
            if browser_data_dir is not None
            else current_dir / BROWSER_DATA_DEFAULT_DIR / self._browser_name
        )
        self._browser_installation_dir = (
            Path(browser_installation_dir)
            if browser_installation_dir is not None
            else current_dir / BROWSER_DEFAULT_INSTALLATION_DIR
        )
        self._executable_path = self._find_executable()
        if self._executable_path is None:
            success = self._install()
            if not success:
                raise RuntimeError("Failed to install browser")
            self._executable_path = self._find_executable()

        self._playwright = None

    def start(self) -> None:
        if self._playwright is not None:
            raise RuntimeError("Playwright already started")

        self._playwright = sync_playwright().start()
        engine = getattr(self._playwright, self._browser_name)
        try:
            self._browser = engine.launch_persistent_context(
                user_data_dir=self._browser_data_dir,
                headless=self.headless,
                executable_path=self._executable_path,
            )
        except Exception as e:
            self._playwright.stop()
            raise RuntimeError(f"Failed to start browser: {e}")

    def stop(self) -> None:
        if self._playwright is None:
            raise ValueError("Playwright not started")
        self._playwright.stop()
        self._playwright = None
        del self._browser

    def __enter__(self) -> "EasyPlaywright":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
        if isinstance(exc_val, TimeoutError):
            return False
        return True

    def _install(self, with_deps: bool = False) -> bool:
        driver_executable, driver_cli = compute_driver_executable()

        env = get_driver_env()
        env.update({"PLAYWRIGHT_BROWSERS_PATH": str(self._browser_installation_dir)})

        args = [driver_executable, driver_cli, "install", self._browser_name]
        if with_deps:
            args.append("--with-deps")

        completed_process = run(
            args, env=env, capture_output=True, text=True, check=False
        )

        return completed_process.returncode == 0

    def _find_executable(self) -> Path | None:
        browser_paths = sorted(
            self._browser_installation_dir.glob(f"{self._browser_name}-*")
        )
        if len(browser_paths) == 0:
            return None
        latest_browser_path = browser_paths[-1]
        verification_file = latest_browser_path / "INSTALLATION_COMPLETE"
        if not verification_file.exists():
            return None
        executable_path = latest_browser_path / self._browser_executable
        return executable_path

    def _is_installed(self) -> bool:
        return self._find_executable() is not None

    ######################################################################
    # Properties
    ######################################################################

    @property
    def browser_type(self) -> BrowserType:
        return self._browser_type

    @property
    def headless(self) -> bool:
        return self._headless

    @property
    def browser(self):
        return self._browser
