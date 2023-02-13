#
#  syscall_analysis.py
#  caladium
#
#  Created by Declan Kelly on 28-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import collections, json, struct, sys, threading

def output_json(json_obj):
    globals()["stdout_lock"].acquire()
    json_obj_bytes = json.dumps(json_obj).encode()
    sys.stdout.buffer.write(struct.pack(">I", len(json_obj_bytes)))
    sys.stdout.buffer.write(json_obj_bytes)
    globals()["stdout_lock"].release()

def send_message(text):
    output_json({"type": "message", "text": text})

def send_progress(value):
    output_json({"type": "progress", "value": value})

def send_state(state):
    output_json({"type": "state", "state": state})

def inc_analysis_count():
    globals()["count_lock"].acquire()
    globals()["analysis_count"] += 1
    globals()["count_lock"].release()

def fetch_next_syscall():
    globals()["deque_lock"].acquire()
    syscall_deque = globals()["syscall_deque"]
    syscall = syscall_deque.pop() if len(syscall_deque) > 0 else None
    globals()["deque_lock"].release()
    return syscall

def analysis_thread_func(malicious_pattern_list):
    while syscall := fetch_next_syscall():
        for pattern in malicious_pattern_list:
            if pattern in syscall:
                send_message(pattern + ", " + syscall)
        inc_analysis_count()

def main(argv):
    def get_file_lines(file_location):
        with open(file_location) as file_handle:
            return file_handle.readlines()

    if len(argv) != 2: return
    syscall_file_location, malicious_pattern_file_location = argv

    syscall_list = get_file_lines(syscall_file_location)
    malicious_pattern_list = get_file_lines(malicious_pattern_file_location)

    globals()["count_lock"], globals()["deque_lock"], globals()["stdout_lock"] = [threading.Lock()] * 3
    globals()["analysis_count"], globals()["syscall_deque"] = 0, collections.deque(syscall_list)

    for _ in range(10): threading.Thread(target=analysis_thread_func, args=[malicious_pattern_list]).start()
    while globals()["analysis_count"] < len(syscall_list): ...

if __name__ == "__main__":
    main(sys.argv[1:])

