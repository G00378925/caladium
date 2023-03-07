# 16:50 27-02-2023

import os, sys, threading

import caladium

def main(argv):
    if len(argv) < 2: return
    file_name = argv[1]

    clamscan = os.environ["ProgramFiles(x86)"] + "\\ClamWin\\bin\\clamscan.exe"

    if not os.path.exists(clamscan):
        caladium.send_message("ClamWin not installed")
        return
    
    if not os.path.exists(file_name):
        caladium.send_message("File not found")
        return
    
    clamscan_result = os.popen(f"\"{clamscan}\" {file_name}").read()
    if "Infected files: 0" in clamscan_result:
        caladium.send_message("No threats found")
    else:
        caladium.send_message("Malware detected")

if __name__ == "__main__":
    main(sys.argv)
