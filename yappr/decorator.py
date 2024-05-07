import os
import sys
import tkinter as tk
import traceback
from argparse import ArgumentParser
from threading import Thread
from tkinter.messagebox import showerror  # type: ignore
from typing import Any
from typing import Callable
from typing import ParamSpec

from yappr import logger
from yappr.updater import Updater

Param = ParamSpec("Param")


def yappr(
    updater: Updater,
) -> Callable[[Callable[Param, Any]], Callable[Param, None]]:

    def decorator(
        func: Callable[Param, Any],
    ) -> Callable[Param, None]:

        def wrapped(*args: Param.args, **kwargs: Param.kwargs) -> None:
            # Initialize updater, updater needs to start as
            # soon as the script starts
            parser = ArgumentParser()
            parser.add_argument("--no-updater", action="store_true")
            cmd_args, _ = parser.parse_known_args(["--no-updater"])
            if not cmd_args.no_updater:
                Thread(target=updater.check_for_updates_loop).start()

            while True:
                try:
                    # Import non-standard libraries only after
                    # updater script has started
                    out = func(*args, **kwargs)

                    # Wait until exit flag is set
                    updater.exit_flag.wait()
                    logger.info("Gracefully shutting down...")

                    # If exit flag was set by user, stop the script
                    if not updater.new_update_flag.is_set():
                        return

                    # if exit flag was set by updater
                    argv = sys.executable, *sys.argv
                    # add quotes to fix file not found
                    # error in windows
                    argv = ['"' + a + '"' for a in argv]
                    os.execl(sys.executable, *argv)
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
                        updater.exit_flag.set()
                        return

        return wrapped

    return decorator
