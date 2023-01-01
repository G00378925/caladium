#
#  database.py
#  caladium
#
#  Created by Declan Kelly on 01-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import os

import pycouchdb

couchdb_server = None
if not couchdb_server:
    couchdb_server = pycouchdb.Server(os.environ["COUCHDB_CONNECTION_STR"])

def get_database(database_name):
    try: return couchdb_server.database(database_name)
    except: return couchdb_server.create(database_name)

def get_caladium_collection(collection_name):
    all_elements = get_database(collection_name).all(as_list=True)
    return {document["id"]: document["doc"] for document in all_elements}

