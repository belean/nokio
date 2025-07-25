import json
import sys
import re
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder
from nokio.model.transaction import Transaction

"""Modul bokio_import manages the import and transform from Bokio into Nokio. It is mainly responsible for 2 things:
1. Import the account balances at start of the year and transform into Json.
2. Import the transactions, validate and transform into Json

Raises:
    RuntimeError: _description_

Returns:
    list[dict]: A list of transaction dicts
"""


def transform_bokio_import(sie_file: Path):
    """Split the SIE file in separate rows"""
    tot: dict = dict(IB={}, UB={}, RES={}, KONTO={}, META={"RAR": {}}, TRANS={})

    # for each row type map a function dealing with type
    row_mapper = {
        "#KONTO": convert_KONTO,
        "#SRU": convert_KONTO,
        "#IB": convert_IB,
        "#UB": convert_UB,
        "#RES": convert_RES,
        "#GEN": convert_META,
        "#ORGNR": convert_META,
        "#FNAMN": convert_META,
        "#RAR": convert_META,
        "#KPTYP": convert_META,
        "#FORMAT": convert_META,
        # "#dummy": lambda x: x,
    }

    with open(sie_file, "r") as fp:
        content = fp.read().split("\n")
        for idx, row in enumerate(content):
            # row = fp.readline()
            if row == "" or row[:4] == "#VER":
                break
            items = row.strip().split()
            row_mapper.get(items[0], lambda x, y: y)(tot, row)
        # #VER is multiline blocks '{', '}'.
        ver_match = re.search(r"#VER.*}", "\n".join(content[idx:]), re.DOTALL)
        trans_list = ver_match.group(0).split("#VER")
        for trans in trans_list:
            if len(trans) > 0:
                result = convert_trans(trans)
                tot["TRANS"][result.verificate] = result.model_dump(
                    exclude="verificate"
                ) | {"org_nr": tot["META"]["ORGNR"]}
    return tot


def write_bokio_import(sie_file: Path, tot: dict):
    (sie_file.parent / "out").mkdir(exist_ok=True)
    file_path = sie_file.parent / "out" / sie_file.with_suffix(".jsonc").name
    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as fj:
        json.dump(
            jsonable_encoder(tot),
            fj,
            ensure_ascii=False,
            indent=2,
            # default=serialize_datetime,
        )


def convert_trans(trans: str):
    account = None
    result = {}
    for idx, line in enumerate(trans.split("\n")):
        if line == "":
            break
        elif line[:4] == ' "V"':
            account = {}
            # Split by '"' and remove empty elements
            meta_data = list(filter(None, [b.strip() for b in line.split('"')]))
            result["verificate"] = meta_data[1]
            result["date"] = (
                datetime.strptime(meta_data[2], "%Y%m%d").date().isoformat()
            )
            result["name"] = meta_data[3]
            result["recorded_at"] = datetime.strptime(
                meta_data[4], "%Y%m%d"
            ).isoformat()
            print(idx, "ver")
        elif line[:1] == "{":
            is_active = True
            print(idx, "start")
        elif line[:1] == "}":
            is_active = False
            print(idx, "stop")
        elif is_active:
            # ex line == "#TRANS 1930 {} -6250.00"
            l_line: list = line.strip().split()
            if float(l_line[3]) <= 0:
                account[f"{l_line[1]}K"] = account.get(f"{l_line[1]}K", 0) + float(
                    l_line[3]
                ) * (-1)
            else:
                account[f"{l_line[1]}D"] = account.get(f"{l_line[1]}D", 0) + float(
                    l_line[3]
                )
    result["account"] = account
    return Transaction(**result)


def convert_META(tot: dict, row: str):
    items = row.split()
    if items[0] == "#FNAMN":
        tot["META"][items[0].strip("#")] = row.split('"')[1]
    elif items[0] == "#RAR":
        tot["META"]["RAR"][items[1]] = {"from": items[2], "to": items[3]}
    else:
        tot["META"][items[0].strip("#")] = items[1]


def convert_KONTO(tot: dict, row: str):
    """Takes
          #KONTO 1010 "Utvecklingsutgifter"
          or
          #SRU 1010 7201
      and returns
      {
          "1010": {
          "Namn": "Utvecklingsutgifter",
          "SRU":7201}
      }

    Args:
        konto_rows (str): _description_

    Returns:
        _type_: _description_
    """
    # dmap: dict = {}
    # for row in row.strip().split("\n"):
    items = row.split()
    if items[0] == "#KONTO":
        row.split('"')
        tot["KONTO"][items[1]] = tot["KONTO"].get(items[1], {}) | {
            "Namn": row.split('"')[1]
        }
    elif items[0] == "#SRU":
        tot["KONTO"][items[1]] = tot["KONTO"].get(items[1], {}) | {"SRU": items[2]}
    # return dmap
    # konto: list = list(map(lambda x: x.strip('"'), konto_rows.split()))
    # return {konto[1]: {"Namn": konto[2], "SRU": konto[5]}}


def convert_IB(tot: dict, row: str):
    """Convert
      #IB -1 1630 10262.00
      #IB 0 1630 -2.00
      #IB -1 1650 432.00
      #IB 0 1650 1027.00
    To
    #IB: {
      "1630":
          {"-1": "10262.00",
          "0": "-2.00"},
      "1650":
          {"-1": "432.00",
           "0": "1027.00"}
    }
    """

    # for row in ib_rows.strip().split("\n"):
    items = row.split()
    tot["IB"][items[2]] = tot["IB"].get(items[2], {}) | {items[1]: items[3]}


def convert_UB(tot: dict, row: str) -> dict:
    """Rows that starts with #UB converts to a dict and later json
    #UB -1 2614 -1861.80
    #UB 0 2614 -1886.58
    #UB -2 2640 0.00
    To { "2614": {  "-1": "-1861.80",
                    "0" : "-1886.58"},
         "2640": {"-2": "0.00"}
        }
    """
    items = row.split()
    tot["UB"][items[2]] = tot["UB"].get(items[2], {}) | {items[1]: items[3]}


def convert_RES(tot: dict, row: str):
    """Rows that starts with #RES converts to a dict and later json"""
    items = row.split()
    tot["RES"][items[2]] = tot["RES"].get(items[2], {}) | {items[1]: items[3]}


def get_incoming_balance() -> pd.DataFrame:
    """Get the incoming balance from the IB dict"""
    books_2023 = transform_bokio_import(
        Path("data/Bokföring - Bokio - 5569979445") / "5569979445_2023.se"
    )
    df_ib = pd.DataFrame.from_records(books_2023["IB"]).T
    df_ib = df_ib.rename(columns={"-1": "2022", "-2": "2021", "0": "2023"}).drop(
        columns=["-5", "-4", "-3", "-6"]
    )
    df_ib = df_ib.astype(float).fillna(0.0)
    df_ib = df_ib[~(df_ib == 0.0).all(axis=1)]
    return df_ib


def run(sie_file: Path):
    tot = transform_bokio_import(sie_file)
    write_bokio_import(sie_file, tot)


if __name__ == "__main__":
    # Interactive run
    run(Path("data/Bokföring - Bokio - 5592945496") / "5592945496_2023.se")
    # generate_general_ledger(
    #    Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    # )
