#
#  syscall_analysis.py
#  caladium
#
#  Created by Declan Kelly on 28-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import collections, sys, threading

import caladium_resp as caladium

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

def send_message(text):
    globals()["output"][0] += text

# This is the function that is run by each analysis thread
def analysis_thread_func(malicious_pattern_list):
    while syscall := fetch_next_syscall():
        for pattern in malicious_pattern_list:
            if pattern in syscall:
                caladium.send_message(pattern + ", " + syscall, send_message)
                caladium.send_state("malware_detected", send_message)
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
    globals()["count_lock"], globals()["deque_lock"] = [threading.Lock()] * 2
    globals()["analysis_count"], globals()["syscall_deque"] = 0, collections.deque(syscall_list)

    # Setup the output buffer
    globals()["output"] = [bytes()]

    # Spawn analysis threads
    for _ in range(10): threading.Thread(target=analysis_thread_func, args=[malicious_pattern_list]).start()
    while globals()["analysis_count"] < len(syscall_list): ...

    # Send the output to the client
    if len(globals()["output"][0]) == 0:
        caladium.send_message("No threats found")
    sys.stdout.buffer.write(globals()["output"][0])

if __name__ == "__main__":
    main(sys.argv[1:])

