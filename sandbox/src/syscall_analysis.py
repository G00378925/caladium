#
# This script is used to analyse the syscalls of a process.
# python3 syscall_analysis.py <syscall_file> <malicious_pattern_file>
#

import multiprocessing, sys

import caladium_resp as caladium

def analysis_worker(syscall_queue, malicious_patterns):
    while True:
        # Fetch a syscall from the queue
        try: syscall = syscall_queue.get(timeout=1)
        except: break
        for pattern in malicious_patterns:
            # Check for a pattern match
            if pattern in syscall:
                caladium.send_message(f"[-] A malicious pattern has been detected: {pattern}")
                caladium.send_state("malware_detected")

def main(argv):
    if len(argv) != 2: return
    syscall_file_location, malicious_pattern_file_location = argv

    with open(syscall_file_location, encoding="utf-8") as syscall_file:
        syscalls = syscall_file.readlines()

    with open(malicious_pattern_file_location, encoding="utf-8") as pattern_file:
        malicious_patterns = set(pattern_file.readlines())

    worker_count = 40 # Number of worker threads
    syscall_queue = (multiprocessing.Manager()).Queue()

    # Put all syscalls into the queue
    for syscall in syscalls: syscall_queue.put(syscall)

    pool = multiprocessing.Pool(processes=worker_count)
    # Spawn worker processes to process the syscalls
    for _ in range(worker_count):
        pool.apply_async(analysis_worker, (syscall_queue, malicious_patterns))

    pool.close()
    pool.join()

if __name__ == "__main__":
    main(sys.argv[1:])