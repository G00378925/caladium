# 16:50 27-02-2023

import os, sys

import caladium_resp as caladium

def main(argv):
    if len(argv) < 2: return
    file_name = argv[1]

    clamscan = os.environ["ProgramFiles(x86)"] + "\\ClamWin\\bin\\clamscan.exe"

    # Check if ClamWin is installed
    if not os.path.exists(clamscan):
        caladium.send_message("ClamWin not installed")
        return

    # Check if the file exists
    if not os.path.exists(file_name):
        caladium.send_message("File not found")
        return
    
    # Scan the file using ClamWin
    clamscan_result = os.popen(f"\"{clamscan}\" {file_name}").read()
    if "Infected files: 0" in clamscan_result:
        caladium.send_message("[+] Static analysis: No malware detected")
    else:
        caladium.send_message("[-] Static analysis: Malware detected")
        caladium.send_state("malware_detected")

if __name__ == "__main__":
    main(sys.argv)
