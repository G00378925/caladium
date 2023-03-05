# 16:50 27-02-2023

import os, sys

import caladium

def main(argv):
    if len(argv) < 2: return

    clamscan = os.environ["ProgramFiles(x86)"] + "ClamWin\bin\clamscan.exe"

    if not os.path.exists(clamscan):
        caladium.send_message("ClamWin not installed")
        return

if __name__ == "__main__":
    main(sys.argv)
