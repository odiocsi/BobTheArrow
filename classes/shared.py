import os
import json
import config

json_path = config.database_path
if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
    database = {}
else:
    with open(json_path, 'r') as db_json:
        database = json.load(db_json)