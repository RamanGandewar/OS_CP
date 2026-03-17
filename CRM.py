import os
import signal
import subprocess
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "Backend"
FRONTEND_DIR = ROOT / "Frontend"
BACKEND_VENV_PYTHON = BACKEND_DIR / "venv" / "Scripts" / "python.exe"


def stream_output(process, prefix):
    for line in process.stdout:
        print(f"[{prefix}] {line.rstrip()}")


def start_process(command, workdir):
    return subprocess.Popen(
        command,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=False,
    )


def main():
    npm_command = "npm.cmd" if os.name == "nt" else "npm"
    backend_python = str(BACKEND_VENV_PYTHON) if BACKEND_VENV_PYTHON.exists() else sys.executable
    backend = start_process([backend_python, "app.py"], BACKEND_DIR)
    frontend = start_process([npm_command, "start"], FRONTEND_DIR)

    threads = [
        threading.Thread(target=stream_output, args=(backend, "backend"), daemon=True),
        threading.Thread(target=stream_output, args=(frontend, "frontend"), daemon=True),
    ]

    for thread in threads:
        thread.start()

    print("Sales CRM is starting with Phase 9 Final Integration Dashboard enabled.")
    print(f"Backend Python: {backend_python}")
    print("Backend: http://127.0.0.1:5000")
    print("Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop both services.")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        for process in (frontend, backend):
            if process.poll() is None:
                process.send_signal(signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGTERM)
        for process in (frontend, backend):
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
