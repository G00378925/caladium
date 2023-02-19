#
#  syscall_analysis.py
#  caladium
#
#  Created by Declan Kelly on 28-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import collections, json, struct, sys, threading

# Call this to send JSON back to the client
def output_json(json_obj):
    globals()["stdout_lock"].acquire()
    json_obj_bytes = json.dumps(json_obj).encode()
    sys.stdout.buffer.write(struct.pack(">I", len(json_obj_bytes)))
    sys.stdout.buffer.write(json_obj_bytes)
    globals()["stdout_lock"].release()

# Send general text messages to the client
def send_message(text):
    output_json({"type": "message", "text": text})

# Send progress updates to the client, this is a value between 0 and 100
def send_progress(value):
    output_json({"type": "progress", "value": value})

# Send the current state of the analysis to the client
def send_state(state):
    output_json({"type": "state", "state": state})

# Increment the count of analysed syscalls
def inc_analysis_count():
    globals()["count_lock"].acquire()
    globals()["analysis_count"] += 1
    globals()["count_lock"].release()

# Fetch the next syscall to analyse
def fetch_next_syscall():
    globals()["deque_lock"].acquire()
    syscall_deque = globals()["syscall_deque"]
    syscall = syscall_deque.pop() if len(syscall_deque) > 0 else None
    globals()["deque_lock"].release()
    return syscall

# This is the function that is run by each analysis thread
def analysis_thread_func(malicious_pattern_list):
    while syscall := fetch_next_syscall():
        for pattern in malicious_pattern_list:
            if pattern in syscall:
                send_message(pattern + ", " + syscall)
        inc_analysis_count()

def main(argv):
    # Read the file lines into a list
    def get_file_lines(file_location):
        with open(file_location) as file_handle:
            return file_handle.readlines()

    if len(argv) != 2: return
    syscall_file_location, malicious_pattern_file_location = argv

    # Syscall and list of patterns to search for
    syscall_list = get_file_lines(syscall_file_location)
    malicious_pattern_list = get_file_lines(malicious_pattern_file_location)

    # Locks for thread synchronisation
    globals()["count_lock"], globals()["deque_lock"], globals()["stdout_lock"] = [threading.Lock()] * 3
    globals()["analysis_count"], globals()["syscall_deque"] = 0, collections.deque(syscall_list)

    # Spawn analysis threads
    for _ in range(10): threading.Thread(target=analysis_thread_func, args=[malicious_pattern_list]).start()
    while globals()["analysis_count"] < len(syscall_list): ...

if __name__ == "__main__":
    main(sys.argv[1:])

