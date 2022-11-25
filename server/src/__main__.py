#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import sys

import flask, requests

app = flask.Flask(__name__)

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

@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    request_data = flask.request.get_data()
    print(f"Received {len(request_data)} byte(s)")
    return str()

def after_request(response_obj):
    response_obj.headers.add("Access-Control-Allow-Headers", '*')
    response_obj.headers.add("Access-Control-Allow-Methods", '*')
    response_obj.headers.add("Access-Control-Allow-Origin", '*')
    return response_obj

def main(argv):
    port_number = int(argv[1]) if len(argv) > 1 else 8080
    app.after_request(after_request)
    app.run(host="0.0.0.0", port=port_number)

if __name__ == "__main__":
    main(sys.argv)

