import re
from enum import Enum
from typing import List


def clean_name(name, allow_characters: List[str] = []) -> str:
    """ method to clean names

    Args:
        name (str): name to be cleaned
        allow_characters (List[str], optional): List of allowed characters. Defaults to [].

    Returns:
        str: cleaned named
    """
    for char in ['\ufeff', '\uFEFF', '"', '$', '\n', '\r', '\t']:
        name = name.replace(char, '')

    indexes_of_allowed_characters = {}
    for allowed_char in allow_characters:
        if allowed_char not in indexes_of_allowed_characters:
            indexes_of_allowed_characters[allowed_char] = []

        for idx, char in enumerate(name):
            if char == allowed_char:
                indexes_of_allowed_characters[allowed_char].append(idx)

    name = re.sub(r'\W', '_', name)

    for allowed_char, indexes in indexes_of_allowed_characters.items():
        for idx in indexes:
            name = replacer(name, allowed_char, idx)

    if name and re.match(r'\d', name[0]):
        name = f'letter_{name}'
    return name.lower()


def camel_to_snake_case(name) -> str:
    """ method to convert camel case to snake case

    Args:
        name (str): string to be transformed

    Returns:
        str: transformed string
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def replacer(org_str, newstring, index, nofail=False):
    """ method to construct new string
    """
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(org_str)):
        raise ValueError('index outside given string')

    # if not error, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + org_str
    if index > len(org_str):  # add it to the end
        return org_str + newstring

    # insert the new string between 'slices' of the original
    return org_str[:index] + newstring + org_str[index + 1:]


def format_enum(var: Enum | str):
    """ method to return enum value or str

    Returns:
        str: value of enum or str
    """
    return var.value if isinstance(var, Enum) else var
