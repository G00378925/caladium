#
#  database.py
#  caladium
#
#  Created by Declan Kelly on 01-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, os, sys

import pycouchdb

if not os.environ.get("COUCHDB_CONNECTION_STR", None):
    sys.stderr.write("COUCHDB_CONNECTION_STR environmental variable must be set\n")
    sys.exit(0)

couchdb_server = pycouchdb.Server(os.environ["COUCHDB_CONNECTION_STR"])

def get_database(database_name):
    try: return couchdb_server.database(database_name)
    except: return couchdb_server.create(database_name)

def get_caladium_collection(database_name):
    all_elements = get_database(database_name).all(as_list=True)
    return {document["id"]: document["doc"] for document in all_elements}

class DatabaseRecord:
    def __init__(self, items):
        self.fields = {}
        if type(items) == dict: items = items.items()

        for field_name, field_value in items:
            self.fields[field_name] = field_value

    def get(self, field_name):
        return self.fields[field_name]

    def set(self, field_name, new_value):
        self.fields[field_name] = new_value
        self.fields["_rev"] = get(self.__class__, self.fields["_id"]).get("_rev")

        try: get_database(self.database_name).save(self.fields)
        except: pass

    def delete(self):
        get_database(self.database_name).delete(self.fields["_id"])

    def __str__(self):
        return json.dumps(self.fields)

def get(record_class, record_id):
    if items := get_database(record_class.database_name).get(record_id).items(): return record_class(items)
    else: return None

def create(record_class, record_dict):
    return record_class(get_database(record_class.database_name).save(record_dict).items())

