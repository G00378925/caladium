# 16:56 27-02-2023

import json, struct, sys

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
