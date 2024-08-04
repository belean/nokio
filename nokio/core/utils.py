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
