# WARNING: ONLY IMPORT STANDARD LIBRARY
# HERE, THIS REDUCES THE CHANCES OF SCRIPT CRASHING
import os
import sys
import tkinter as tk
import traceback
from argparse import ArgumentParser
from threading import Event
from threading import Thread
from tkinter.messagebox import showerror  # type: ignore
from typing import Any
from typing import Callable
from typing import ParamSpec

Param = ParamSpec("Param")


def yappr(
    pkg_name: str,
    exit_flag: Event,
    new_update_flag: Event,
    first_update_interval: float = 10,
    update_interval: float = 900,
) -> Callable[[Callable[Param, Any]], Callable[Param, None]]:

    def decorator(
        func: Callable[Param, Any],
    ) -> Callable[Param, None]:

        def wrapped(*args: Param.args, **kwargs: Param.kwargs) -> None:
            # WARNING: ONLY USE STANDARD LIBRARY
            # AND UPDATER MODULE HERE, THIS REDUCES THE
            # CHANCES OF SCRIPT CRASHING
            from yappr import logger
            from yappr.updater import Updater

            # Initialize updater, updater needs to start as
            # soon as the script starts
            updater = Updater(
                pkg_name,
                first_update_interval,
                update_interval,
                exit_flag,
                new_update_flag,
            )
            parser = ArgumentParser()
            parser.add_argument("-nu", "--no-updater", action="store_true")
            cmd_args, _ = parser.parse_known_args()
            if not cmd_args.no_updater:
                Thread(target=updater.check_for_updates_loop).start()

            while True:
                try:
                    # Import non-standard libraries only after
                    # updater script has started
                    out = func(*args, **kwargs)

                    # Wait until exit flag is set
                    exit_flag.wait()
                    logger.info("Gracefully shutting down...")

                    # If exit flag was set by user, stop the script
                    if not new_update_flag.is_set():
                        return

                    # if exit flag was set by updater
                    os.execl(sys.executable, sys.executable, *sys.argv)
                except Exception:
                    logger.exception("Unhandled Exception")
                    root = tk.Tk()
                    root.withdraw()
                    root.after(30000, root.destroy)
                    out = showerror(
                        "Unhandled Exception",
                        traceback.format_exc(),
                        parent=root,
                    )
                    if out == "ok":
                        exit_flag.set()
                        return

        return wrapped

    return decorator
