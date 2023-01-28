#
#  syscall_analysis.py
#  caladium
#
#  Created by Declan Kelly on 28-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, struct, sys

def output_json(json_obj):
    json_obj_bytes = json.dumps(json_obj).encode()
    sys.stdout.write(struct.pack(">I", len(json_obj_bytes)))
    sys.stdout.write(json_obj_bytes)

def send_message(text):
    output_json({"type": "message", "text", text})

def send_progress(value):
    output_json({"type": "progress", "value", value})

def send_state(state):
    output_json({"type": "state", "state", state})

def main(argv):
    if len(argv) < 2: return
    syscall_file_location, malicious_pattern_file_location = argv

    with open(syscall_file_location) as syscall_file_handle:
        syscall_list = syscall_file_handle.readlines()

if __name__ == "__main__":
    main(sys.argv[1:])

