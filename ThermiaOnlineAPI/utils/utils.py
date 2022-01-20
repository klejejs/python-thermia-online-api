def get_dict_value_safe(dictionary, key, default=None):
    if dictionary is None or key not in dictionary:
        return default
    return dictionary[key]
