# 02:47 24-03-2023

import collections, os, sys, uuid

import flask, openai, requests

openai.api_key = os.environ.get("OPENAI_API_KEY", None)
if not openai.api_key:
    sys.stderr.write("You must have the OPENAI_API_KEY env set\n")
    sys.exit(1)

# Generation of the initial prompt
initial_prompt = """
You are CaladiumBot, you will answer questions about the README listed below:
"""
initial_prompt += requests.get("https://raw.githubusercontent.com/G00378925/caladium/main/README.md").text

question_limit_per_ip, total_question_count = 30, 0
question_count = collections.defaultdict(lambda: 0)
conversations = collections.defaultdict(lambda: [{"role": "system", "content": initial_prompt}])

# Log HTTP requests to log.txt
def write_to_log(ip, question):
    log = open("log.txt", "a+")
    log.write(f"{ip}: {question}\n")
    log.close()

app = flask.Flask(__name__)

@app.post("/api/ask_question")
def ask_question():
    global question_limit_per_ip, total_question_count

    # Safety measure, to avoid my credits being drained
    if total_question_count >= 100: sys.exit(0)
    total_question_count += 1

    if question_count[flask.request.remote_addr] > question_limit_per_ip: return

    question = flask.request.json.get("question", "")
    conversation_id = flask.request.json.get("conversation_id", str(uuid.uuid1()))
    if len(question) == 0: return {"answer": "Empty questions, waste resources"}
    write_to_log(flask.request.remote_addr, question) # Write each question to log file

    # Append the question and answer to the conversation dictionary
    conversations[conversation_id].append({"role": "user", "content": question})
    answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", \
        messages=conversations[conversation_id]).choices[0].message.content
    conversations[conversation_id].append({"role": "assistant", "content": question})

    question_count[flask.request.remote_addr] += 1
    return {"answer": answer, "conversation_id": conversation_id}

# Used to apply CORS headers to every response
def after_request(response_obj):
    response_obj.headers.add("Access-Control-Allow-Headers", '*')
    response_obj.headers.add("Access-Control-Allow-Methods", '*')
    response_obj.headers.add("Access-Control-Allow-Origin", '*')
    return response_obj

def main(argv):
    app.after_request(after_request) # Add response handlers
    app.run(host="0.0.0.0", port=3389, ssl_context=("crt.pem", "key.pem"))

if __name__ == "__main__":
    main(sys.argv)
