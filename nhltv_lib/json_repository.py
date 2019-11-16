import json
import os

# LIST


def ensure_json_list_exists(listname):
    if not os.path.exists(listname):
        with open(listname, "w") as f:
            json.dump(list(), f)


def read_json_list(listname):
    listname += ".json"
    ensure_json_list_exists(listname)
    with open(listname, "r") as f:
        return json.load(f)


# DICT


def ensure_json_dict_exists(dictname):
    if not os.path.exists(dictname):
        with open(dictname, "w") as f:
            json.dump(dict(), f)


def read_json_dict(dictname):
    dictname += ".json"
    ensure_json_dict_exists(dictname)
    with open(dictname, "r") as f:
        return json.load(f)


def add_to_json_dict(dictname, addition):
    dict_ = read_json_dict(dictname)
    dictname += ".json"
    with open(dictname, "w") as f:
        dict_.update(addition)
        json.dump(dict_, f)
