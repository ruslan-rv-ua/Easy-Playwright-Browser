from enum import StrEnum
from pathlib import Path
from subprocess import run

from playwright._impl._driver import (
    compute_driver_executable,  # type: ignore
    get_driver_env,
)

BROWSER_DATA_DEFAULT_DIR = "BROWSERS_DATA"
BROWSER_DEFAULT_INSTALLATION_DIR = "INSTALLED_BROWSERS"


class BrowserType(StrEnum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class _EasyPlaywrightBase:
    def __init__(
        self,
        browser_type: BrowserType = BrowserType.CHROMIUM,
        headless: bool = True,
        browser_data_dir: Path | str | None = None,
        browser_installation_dir: Path | str | None = None,
    ) -> None:
        self._browser_type = browser_type
        self._browser_executable = self._get_browser_executable(browser_type)

        self._headless = headless

        current_dir = Path(__file__).resolve().parent
        self._browser_data_dir = (
            Path(browser_data_dir)
            if browser_data_dir is not None
            else current_dir / BROWSER_DATA_DEFAULT_DIR / self.browser_name
        )
        self._browser_installation_dir = (
            Path(browser_installation_dir)
            if browser_installation_dir is not None
            else current_dir / BROWSER_DEFAULT_INSTALLATION_DIR
        )

        self._playwright = None

    def install_browser(self, with_deps: bool = False) -> bool:
        driver_executable, driver_cli = compute_driver_executable()

        env = get_driver_env()
        env.update({"PLAYWRIGHT_BROWSERS_PATH": str(self._browser_installation_dir)})

        args = [driver_executable, driver_cli, "install", self.browser_name]
        if with_deps:
            args.append("--with-deps")

        completed_process = run(
            args, env=env, capture_output=True, text=True, check=False
        )

        return completed_process.returncode == 0

    def _find_executable(self) -> Path | None:
        browser_paths = sorted(
            self._browser_installation_dir.glob(f"{self.browser_name}-*")
        )
        if len(browser_paths) == 0:
            return None
        latest_browser_path = browser_paths[-1]
        verification_file = latest_browser_path / "INSTALLATION_COMPLETE"
        if not verification_file.exists():
            return None
        executable_path = latest_browser_path / self._browser_executable
        return executable_path

    def is_browser_installed(self) -> bool:
        return self._find_executable() is not None

    def _check_before_start(self) -> None:
        if self._playwright is not None:
            raise RuntimeError("Playwright already started")
        if not self.is_browser_installed():
            raise RuntimeError(
                f"Browser `{self.browser_name}` not installed. Call `install_browser` method first."
            )

    def _check_before_stop(self) -> None:
        if self._playwright is None:
            raise ValueError("Playwright not started")

    ######################################################################

    @staticmethod
    def _get_browser_executable(browser_type):
        match browser_type:
            case BrowserType.CHROMIUM:
                return "chrome-win/chrome.exe"  # TODO: os specific
            case BrowserType.FIREFOX:
                return "firefox/firefox.exe"
            case BrowserType.WEBKIT:
                return "Playwright.exe"
            case _:
                raise ValueError(f"Unknown browser type: {browser_type}")

    @property
    def browser_type(self) -> BrowserType:
        return self._browser_type

    @property
    def headless(self) -> bool:
        return self._headless

    @property
    def browser(self):
        return self._browser

    @property
    def browser_name(self) -> str:
        return self._browser_type.value
