import importlib.metadata
from subprocess import PIPE
from subprocess import STARTF_USESHOWWINDOW
from subprocess import STARTUPINFO
from subprocess import SW_HIDE
from subprocess import check_output
from subprocess import run
from threading import Event

from yappr import logger

# hide flashing console when using pythonw
startupinfo = STARTUPINFO()
startupinfo.dwFlags |= STARTF_USESHOWWINDOW
startupinfo.wShowWindow = SW_HIDE


class Updater:
    def __init__(
        self,
        package_name: str,
        first_update_interval: float = 10,
        update_interval: float = 900,
        exit_flag: Event = Event(),
        new_update_flag: Event = Event(),
    ):
        self.package_name = package_name
        self.first_update_interval = first_update_interval
        self.update_interval = update_interval
        self.current_version = self.get_version()
        self.exit_flag = exit_flag
        self.new_update_flag = new_update_flag

    def get_version(self) -> str:
        try:
            return importlib.metadata.version(self.package_name)
        except importlib.metadata.PackageNotFoundError:
            return ""

    def update(self):
        logger.info("Collecting new packages...")
        run(
            ["pip", "install", "--upgrade", "project-l"],
            text=True,
            stdout=PIPE,
            stderr=PIPE,
            timeout=30,
            startupinfo=startupinfo,
        )
        logger.info("Successfully downloaded new version.")

    def get_latest_version(self):
        out = check_output(
            ["pip", "index", "versions", self.package_name],
            text=True,
            stderr=PIPE,
            timeout=30,
            startupinfo=startupinfo,
        )
        for line in out.split("\n"):
            line = line.strip()
            if line.startswith("LATEST:"):
                version = line[10:].strip()
                return version
        return ""

    def check_for_updates(self):
        try:
            logger.info("Checking for updates...")
            current = self.current_version
            if not current:
                logger.error("Could not determine the current version.")
                return
            latest = self.get_latest_version()
            if not latest:
                logger.error("Could not determine the latest version.")
                return
            if latest == current:
                logger.info("Already upto date.")
                return
            logger.info(f"New version found: {current} -> {latest}")
            self.update()
            self.new_update_flag.set()
            self.exit_flag.set()
        except Exception:
            logger.exception("Unhandled exception in updater.")

    def check_for_updates_loop(self):
        self.exit_flag.wait(self.first_update_interval)
        while True:
            try:
                if self.exit_flag.is_set():
                    break
                self.check_for_updates()
                self.exit_flag.wait(self.update_interval)
            except Exception:
                logger.exception("Unhandled exception in updater.")
                self.exit_flag.wait(self.update_interval)
