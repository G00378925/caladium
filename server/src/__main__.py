#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import hashlib, json, sys

import flask, requests, uuid

import clients, patterns, tasks, workers

authorisation_tokens, administrator_password = [], hashlib.sha256("root".encode()).hexdigest()

app = flask.Flask(__name__)
app.register_blueprint(clients.clients)
app.register_blueprint(patterns.patterns)
app.register_blueprint(tasks.tasks)
app.register_blueprint(workers.workers)

@app.route("/")
@app.route("/<path:index_path>")
def root_page(index_path=None):
    with open("static/index.html") as index_html_handle:
        return index_html_handle.read()

@app.route("/css/<path:css_file_path>")
def serve_css_file(css_file_path):
    milligram_dist_location = "https://raw.githubusercontent.com/milligram/milligram/master/dist/"
    css_file_dict = {
        "milligram.min.css": {"content_type": "text/css"},
        "milligram.min.css.map": {"content_type": "application/json"}
    }

    if css_file_path in css_file_dict:
        milligram_dist_resp = requests.get(milligram_dist_location + css_file_path).text
        return flask.Response(milligram_dist_resp, headers={"Content-Type": css_file_dict[css_file_path]["content_type"]})
    else:
        return str()

@app.route("/js/<path:js_file_path>")
def serve_js_file(js_file_path):
    return flask.send_from_directory("static/js/", js_file_path)

@app.post("/api/login")
def login_route():
    global authorisation_tokens

    req_body_obj = json.loads(flask.request.get_data())
    username, password = req_body_obj["username"], req_body_obj["password"]

    if username == "root" and administrator_password == hashlib.sha256(password.encode()).hexdigest():
        token = str(uuid.uuid1())
        authorisation_tokens += [token]
        return {"Authorisation": token}
    else:
        return {"message": "Incorrect username or password"}

def get_authorisation_tokens():
    global authorisation_tokens
    return authorisation_tokens

def before_request():
    path, resp_obj = flask.request.path, flask.Response()
    if path.startswith("/api/tasks"):
        if flask.request.headers["Authorisation"] not in clients.get_authorisation_tokens():
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid client authorisation token")
            return resp_obj
    elif path.startswith("/api") and not path.startswith("/api/login"):
        if flask.request.headers["Authorisation"] not in get_authorisation_tokens():
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid authorisation token")
            return resp_obj

def after_request(response_obj):
    response_obj.headers.add("Access-Control-Allow-Headers", '*')
    response_obj.headers.add("Access-Control-Allow-Methods", '*')
    response_obj.headers.add("Access-Control-Allow-Origin", '*')
    return response_obj

def main(argv):
    port_number = int(argv[1]) if len(argv) > 1 else 8080
    app.before_request(before_request)
    app.after_request(after_request)
    app.run(host="0.0.0.0", port=port_number)

if __name__ == "__main__":
    main(sys.argv)

