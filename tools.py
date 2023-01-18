import os
import json


def json2dict(path):
    if not os.path.exists(path) or path[-5:] != ".json":
        print("File path is invalid.")
        return None

    with open(path, 'r') as f:
        return json.loads(f.read())


def dict2json(dict, output_path, encoding="utf-8"):
    with open(output_path, "w", encoding=encoding) as f:
        f.write(json.dumps(dict, indent=4, separators=(',', ':')))

