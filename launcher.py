import platform
import subprocess
import time
import sys
import os

def main():
    os_name = platform.system()
    print(f"Starting IoT Parking System on {os_name}...")
    
    processes = []

    try:
        if os_name == "Windows":
            commands = [
                "cmd /c mosquitto -v",
                "cmd /c call .venv\\Scripts\\activate && cd Backend && uvicorn backend:app --reload",
                "cmd /c call .venv\\Scripts\\activate && python Model/webcam_handler.py" 
            ]
            
            for cmd in commands:
                p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                processes.append(p)

        elif os_name == "Linux":
            commands = [
                "mosquitto -v",
                "source .venv/bin/activate && cd Backend && uvicorn backend:app --reload",
                "source .venv/bin/activate && python3 Model/webcam_handler.py"
            ]
            
            for cmd in commands:
                p = subprocess.Popen(["gnome-terminal", "--wait", "--", "bash", "-c", cmd])
                processes.append(p)

        elif os_name == "Darwin": # macOS
            commands = [
                "mosquitto -v",
                "source .venv/bin/activate && cd Backend && uvicorn backend:app --reload",
                "source .venv/bin/activate && python3 Model/webcam_handler.py"
            ]
            for cmd in commands:
                p = subprocess.Popen(f"""osascript -e 'tell app "Terminal" to do script "{cmd}"'""", shell=True)
                processes.append(p)
                
        else:
            print(f"Unsupported OS: {os_name}")
            sys.exit(1)

        print("\nAll services running.")
        print("Close any of the new terminal windows (or press Ctrl+C here) to shut down the entire system.\n")
        
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(processes.index(p))
                    raise KeyboardInterrupt 
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nTerminal closure or exit detected. Shutting down all services...")
        
        if os_name == "Windows":
            for p in processes:
                try:
                    subprocess.run(
                        f"taskkill /F /T /PID {p.pid}", 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
            subprocess.run("taskkill /IM mosquitto.exe /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        elif os_name in ["Linux", "Darwin"]:
            for p in processes:
                try:
                    p.terminate()
                except Exception:
                    pass

            target_processes = [
                "mosquitto", 
                "uvicorn", 
                "webcam_handler.py"
            ]
            
            for target in target_processes:
                subprocess.run(
                    f"pkill -9 -f '{target}'", 
                    shell=True, 
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL
                )
            
            subprocess.run("killall -9 mosquitto", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
            # On Linux, if gnome-terminal leaves orphan shells behind, this clears them
            if os_name == "Linux":
                subprocess.run("pkill -9 -f 'gnome-terminal'", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        print("all the terminals were closed correctly")

if __name__ == "__main__":
    main()