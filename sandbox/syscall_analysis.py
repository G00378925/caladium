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
    sys.stdout.buffer.write(struct.pack(">I", len(json_obj_bytes)))
    sys.stdout.buffer.write(json_obj_bytes)

def send_message(text):
    output_json({"type": "message", "text": text})

def send_progress(value):
    output_json({"type": "progress", "value": value})

def send_state(state):
    output_json({"type": "state", "state": state})

def get_file_lines(file_location):
    with open(file_location) as file_handle:
        return file_handle.readlines()

def main(argv):
    if len(argv) < 2: return
    syscall_file_location, malicious_pattern_file_location = argv

    send_message("syscall_analysis.py started")

    syscall_list = get_file_lines(syscall_file_location)
    malicious_pattern_list = get_file_lines(malicious_pattern_file_location)

    for pattern in malicious_pattern_list:
        send_message(pattern)

if __name__ == "__main__":
    main(sys.argv[1:])

