def merge_dict(dict_a, dict_b):
    """method to merge two dictionaries together"""
    dict_c = dict_a.copy()
    dict_c.update(dict_b)
    return dict_c
