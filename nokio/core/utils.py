import re
import json


def open_jsonc(file_path: str):
    """Opens a JSONC (with comments) and strips characters between
    /* and
    */
    as well as
        // to the end of line (one line)

    Args:
        file_path (str): Path to jsonc file

    Returns:
        _type_: list of dict
    """
    with open(file_path, "r") as fp:
        file_str = fp.read()
    # Drop between /*...*/
    tmp = re.sub("/\*.*?\*/", "", file_str, flags=re.DOTALL)
    # Drop //...
    return json.loads(re.sub("//.*", "", tmp))


def chunk(it: list, size: int = 1):
    """Divide iteraor into chunks i.e. batches

    Args:
        it (list): list of dicts
        size (int): chunk size

    Yields:
        list[dict]: list of dicts
    """
    for i in range(0, len(it), size):
        yield it[i : i + size]
