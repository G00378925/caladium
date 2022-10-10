#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import sys

import flask

app = flask.Flask(__name__)

@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    request_data = flask.request.get_data()
    print(f"Received {len(request_data)} byte(s)")
    return str()

def main(argv):
    app.run(host="127.0.0.1", port=8080)

if __name__ == "__main__":
    main(sys.argv)

