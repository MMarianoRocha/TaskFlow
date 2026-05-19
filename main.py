import os
import sys
from pathlib import Path

import uvicorn


def _use_exe_directory_as_workdir() -> None:
    if getattr(sys, "frozen", False):
        os.chdir(Path(sys.executable).resolve().parent)


def main() -> None:
    _use_exe_directory_as_workdir()

    from app.app import app

    host = os.getenv("POMODORO_HUB_HOST", "0.0.0.0")
    port = int(os.getenv("POMODORO_HUB_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
