import json


def get_dict_value_safe(dictionary, key, default=None):
    if dictionary is None or key not in dictionary:
        return default
    return dictionary[key]


def pretty_print(json_object):
    print(json.dumps(json_object, indent=4, sort_keys=True))
    print("\n")


def pretty_print_except(json_object, except_keys=[]):
    if json_object is None:
        return

    json_object_copy = json_object.copy()
    for key in except_keys:
        if key in json_object_copy:
            del json_object_copy[key]
    pretty_print(json_object_copy)
