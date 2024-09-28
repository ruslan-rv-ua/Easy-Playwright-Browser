from pathlib import Path
from subprocess import run
from typing import Literal

from playwright._impl._driver import (
    compute_driver_executable,  # type: ignore
    get_driver_env,
)

USER_DATA_DEFAULT_DIR = "USER_DATA"
BROWSERS_INSTALL_DEFAULT_DIR = "INSTALLED_BROWSERS"


class _EasyPlaywrightBase:
    def __init__(
        self,
        browser_name: Literal["chromium", "firefox", "webkit"] = "chromium",
        headless: bool = True,
        user_data_dir: Path | str | None = None,
        browsers_install_dir: Path | str | None = None,
        install_browser: bool = True,
        **kwargs,
    ) -> None:
        self._browser_name = browser_name
        self._headless = headless
        self._browser_executable = self._get_browser_executable_file_relative_path(
            browser_name
        )

        current_dir = Path(__file__).resolve().parent
        if self._user_data_dir is not None:
            self._user_data_dir = Path(self._user_data_dir)
        else:
            self._user_data_dir = current_dir / USER_DATA_DEFAULT_DIR / browser_name
        if browsers_install_dir is not None:
            browsers_install_dir = Path(browsers_install_dir)
        else:
            browsers_install_dir = current_dir / BROWSERS_INSTALL_DEFAULT_DIR
        executable_path = self._find_executable()
        if executable_path is None and install_browser:
            self.install_browser()

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
    def _get_browser_executable_file_relative_path(browser_name):
        match browser_name:
            case "chromium":
                return "chrome-win/chrome.exe"  # TODO: os specific
            case "firefox":
                return "firefox/firefox.exe"
            case "webkit":
                return "Playwright.exe"
            case _:
                raise ValueError(f"Unknown browser name: {browser_name}")

    @property
    def headless(self) -> bool:
        return self._headless

    @property
    def browser_name(self) -> str:
        return self._browser_name
