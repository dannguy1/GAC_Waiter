import subprocess
import os
import signal
import sys

def kill_port(port):
    print(f"Scanning for processes on port {port}...")
    try:
        # Run netstat requires sudo sometimes for process names, but for owned processes it works
        cmd = ["netstat", "-tulpn"]
        output = subprocess.check_output(cmd).decode()
        killed = False
        for line in output.split('\n'):
            if f":{port}" in line and "LISTEN" in line:
                parts = line.split()
                # PID/Name is usually last column, e.g. "1234/node"
                # Find the column with /
                for part in parts:
                    if '/' in part and part.split('/')[0].isdigit():
                        pid = int(part.split('/')[0])
                        print(f"Found PID {pid} on port {port}. Killing...")
                        try:
                            os.kill(pid, signal.SIGKILL)
                            killed = True
                        except ProcessLookupError:
                            print("Process already dead.")
                        except PermissionError:
                            print("Permission denied.")
        
        if not killed:
            print("No matching process found or killed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    kill_port(3000)
