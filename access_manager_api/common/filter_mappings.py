from typing import List


arg_splitter = lambda val: val.split(",")


def get_filter_mappings(mapping_array: List[str], mappings_dict: dict) -> dict:
    mappings = {}
    for f in mapping_array:
        mappings[f] = f

    return mappings | mappings_dict
