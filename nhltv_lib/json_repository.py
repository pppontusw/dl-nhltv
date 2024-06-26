from typing import Union, List, Dict
import json
import os

JSON_FILE_ENDING = ".json"

# LIST


def ensure_json_list_exists(listname: str) -> None:
    if not os.path.exists(listname):
        with open(listname, "w") as f:
            json.dump([], f)


def read_json_list(listname: str) -> List[Union[str, int]]:
    listname += JSON_FILE_ENDING
    ensure_json_list_exists(listname)
    with open(listname, "r") as f:
        return json.load(f)


def add_to_json_list(listname: str, addition: Union[str, int]):
    list_: List[Union[str, int]] = read_json_list(listname)
    listname += JSON_FILE_ENDING
    if addition not in list_:
        with open(listname, "w") as f:
            list_.append(addition)
            json.dump(list_, f)


# DICT


def ensure_json_dict_exists(dictname: str) -> None:
    if not os.path.exists(dictname):
        with open(dictname, "w") as f:
            json.dump({}, f)


def read_json_dict(dictname: str) -> Dict[str, str]:
    dictname += JSON_FILE_ENDING
    ensure_json_dict_exists(dictname)
    with open(dictname, "r") as f:
        return json.load(f)


def add_to_json_dict(dictname: str, addition: dict) -> None:
    dict_: Dict[str, str] = read_json_dict(dictname)
    dictname += JSON_FILE_ENDING
    with open(dictname, "w") as f:
        dict_.update(addition)
        json.dump(dict_, f)
