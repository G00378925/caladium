# 16:56 27-02-2023

import json, struct, sys, threading

# Call this to send JSON back to the client
def output_json(json_obj, output_func=sys.stdout.buffer.write):
    if "stdout_lock" not in globals():
        globals()["stdout_lock"] = threading.Lock()

    globals()["stdout_lock"].acquire()
    json_obj_bytes = json.dumps(json_obj).encode()
    output_func(struct.pack(">I", len(json_obj_bytes)))
    output_func(json_obj_bytes)
    globals()["stdout_lock"].release()

# Send general text messages to the client
def send_message(text):
    output_json({"type": "message", "text": text})

# Send progress updates to the client, this is a value between 0 and 100
def send_progress(value, output_func=None):
    output_json({"type": "progress", "value": value}, output_func)

# Send the current state of the analysis to the client
def send_state(state):
    output_json({"type": "state", "state": state})

