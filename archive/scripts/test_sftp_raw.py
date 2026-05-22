import subprocess
import os

WINSCP_EXE = r"C:\Program Files (x86)\WinSCP\WinSCP.com"
SFTP_SESSION = "cas_hue@10.1.45.10"

def test_raw():
    # TEST 1: LS /
    cmd = [WINSCP_EXE, "/command", f"open {SFTP_SESSION} -hostkey=*", "ls /", "exit"]
    print(f"RUNNING: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True) # Binary capture
    
    with open("winscp_stdout.bin", "wb") as f:
        f.write(res.stdout)
    with open("winscp_stderr.bin", "wb") as f:
        f.write(res.stderr)
        
    print(f"EXIT CODE: {res.returncode}")
    print(f"STDOUT SIZE: {len(res.stdout)}")

if __name__ == "__main__":
    test_raw()
