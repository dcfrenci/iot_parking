import platform
import subprocess
import time
import sys
import os

SERVICE_NAMES = ["mosquitto", "backend", "webcam_handler", "bridge"]

def get_commands(os_name: str) -> list[str]:
    """Return the commands for the current OS."""
    if os_name == "Windows":
        return [
            "mosquitto -v",
            "call conda activate iot_env && cd Backend && uvicorn backend:app --host 0.0.0.0 --reload",
            "call conda activate iot_env && python Model/webcam_handler.py",
            "call conda activate iot_env && python Arduino/bridge.py",
        ]
    elif os_name == "Linux":
        return [
            "mosquitto -v",
            "source .venv/bin/activate && cd Backend && uvicorn backend:app --host 0.0.0.0 --reload",
            "source .venv/bin/activate && python3 Model/webcam_handler.py",
            "source .venv/bin/activate && python3 Arduino/bridge.py",
        ]
    elif os_name == "Darwin":
        return [
            "mosquitto -v",
            "source .venv/bin/activate && cd Backend && uvicorn backend:app --reload",
            "source .venv/bin/activate && python3 Model/webcam_handler.py",
            "source .venv/bin/activate && python3 Arduino/bridge.py",
        ]
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)


def _find_terminal() -> str:
    """
    Return the first available terminal emulator on Linux.
    Preference order: gnome-terminal → xterm.
    Exits with an error if none is found.
    """
    for term in ("gnome-terminal", "xterm"):
        result = subprocess.run(
            ["which", term],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            print(f"  Using terminal emulator: {term}")
            return term
    print("ERROR: No supported terminal emulator found (tried gnome-terminal, xterm).")
    sys.exit(1)


def launch_windows(commands: list[str]) -> list[subprocess.Popen]:
    """Open one new console window per service (Windows)."""
    processes = []
    for name, cmd in zip(SERVICE_NAMES, commands):
        p = subprocess.Popen(
            ["cmd", "/K", f"title {name} && {cmd}"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        processes.append(p)
        print(f"  [{name}] started  (pid={p.pid})")
    return processes


def launch_linux(commands: list[str]) -> list[subprocess.Popen]:
    """Open one terminal window per service (Linux)."""
    term = _find_terminal()
    processes = []

    for name, cmd in zip(SERVICE_NAMES, commands):
        keep_open = f"{cmd}; echo; echo '[{name}] process ended — press Enter to close'; read"

        if term == "gnome-terminal":
            args = [
                "gnome-terminal",
                f"--title={name}",
                "--",
                "bash", "-c", keep_open,
            ]
        else:  # xterm
            args = [
                "xterm",
                "-title", name,
                "-e", f"bash -c {keep_open!r}",
            ]

        p = subprocess.Popen(args)
        processes.append(p)
        print(f"  [{name}] started  (terminal pid={p.pid})")

    return processes


def launch_macos(commands: list[str]) -> list[subprocess.Popen]:
    """Open one Terminal.app tab per service (macOS)."""
    processes = []

    for name, cmd in zip(SERVICE_NAMES, commands):
        # Escape single quotes inside the command for AppleScript embedding
        safe_cmd = cmd.replace("'", "'\\''")
        keep_open = f"{safe_cmd}; echo; echo '[{name}] process ended — press Enter to close'; read"

        applescript = (
            f"tell application \"Terminal\"\n"
            f"    activate\n"
            f"    set w to do script \"echo -n -e '\\\\033]0;{name}\\\\007' && {keep_open}\"\n"
            f"end tell"
        )

        p = subprocess.Popen(["osascript", "-e", applescript])
        processes.append(p)
        print(f"  [{name}] started  (osascript pid={p.pid})")

    return processes


def shutdown_windows(processes: list[subprocess.Popen]):
    """Kill every process tree by PID, then sweep mosquitto by name."""
    print("\nTerminating all services…")
    for name, p in zip(SERVICE_NAMES, processes):
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"  [{name}] terminated")
        except Exception as e:
            print(f"  [{name}] error: {e}")
    # Belt-and-suspenders: kill mosquitto by image name in case it re-spawned
    subprocess.run(
        ["taskkill", "/IM", "mosquitto.exe", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("All services stopped.")


def shutdown_unix(os_name: str):
    """
    Kill services by process name on Linux/macOS.
    Because gnome-terminal / osascript detach immediately, we never held
    a useful PID for the actual service — so pkill by name is the right tool.
    """
    print("\nTerminating all services…")

    targets = ["mosquitto", "uvicorn", "webcam_handler.py", "bridge.py"]
    for target in targets:
        subprocess.run(
            ["pkill", "-9", "-f", target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"  [{target}] killed")

    # Belt-and-suspenders for mosquitto
    subprocess.run(["killall", "-9", "mosquitto"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os_name == "Linux":
        subprocess.run(["pkill", "-9", "-f", "gnome-terminal"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("All services stopped.")


PGREP_PATTERNS: dict[str, str] = {
    "mosquitto":     "mosquitto",
    "backend":       "uvicorn",
    "webcam_handler":"webcam_handler.py",
    "bridge":        "bridge.py",
}

def _is_running_unix(name: str) -> bool:
    """Return True if the service process is found via pgrep."""
    result = subprocess.run(
        ["pgrep", "-f", PGREP_PATTERNS[name]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

def monitor_windows(processes: list[subprocess.Popen]) -> str | None:
    """Uses the real PIDs, to poll them directly."""
    for name, p in zip(SERVICE_NAMES, processes):
        if p.poll() is not None:
            return name
    return None

def monitor_unix() -> str | None:
    """Returns the name of the first service that is no longer running, or None."""
    for name in SERVICE_NAMES:
        if not _is_running_unix(name):
            return name
    return None


def main():
    os_name = platform.system()
    print(f"Starting IoT Parking System on {os_name}…\n")

    commands = get_commands(os_name)

    if os_name == "Windows":
        processes = launch_windows(commands)
    elif os_name == "Linux":
        processes = launch_linux(commands)
    elif os_name == "Darwin":
        processes = launch_macos(commands)
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

    if os_name != "Windows":
        print("Waiting for services to start up…")
        time.sleep(3)

    print("\nAll 4 services are running in separate terminal windows.")
    print("Close any service window (or press Ctrl+C here) to shut everything down.\n")

    try:
        while True:
            if os_name == "Windows":
                dead = monitor_windows(processes)
            else:
                dead = monitor_unix()

            if dead:
                print(f"\n[!] Service '{dead}' stopped — shutting down all services.")
                raise KeyboardInterrupt
            time.sleep(0.75)

    except KeyboardInterrupt:
        print("\nShutdown requested…")
        if os_name == "Windows":
            shutdown_windows(processes)
        else:
            shutdown_unix(os_name)

    print("Goodbye.")


if __name__ == "__main__":
    main()