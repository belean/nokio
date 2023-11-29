import json
from pathlib import Path


def split_SIE(sie_file: Path):
    """Split the SIE file in separate rows"""
    tot: dict = dict()

    row_mapper = {
        "#KONTO": convert_KONTO,
        "#SRU": convert_KONTO,
        "#IB": convert_IB,
        "#UB": convert_UB,
        "#RES": convert_RES,
        # "#dummy": lambda x: x,
    }

    with open(sie_file, "r") as fp:
        while True:
            row = fp.readline()
            if row == "":
                break
            items = row.strip().split()
            row_mapper.get(items[0], lambda x, y: x)(tot, row)


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
        tot[items[1]] = tot.get(items[1], {}) | {"Namn": row.split('"')[1]}
    elif items[0] == "#SRU":
        tot[items[1]] = tot.get(items[1], {}) | {"SRU": items[2]}
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
    {
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
    tot[items[2]] = tot.get(items[2], {}) | {items[1]: items[3]}


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
    tot[items[2]] = tot.get(items[2], {}) | {items[1]: items[3]}


def convert_RES(tot: dict, row: str):
    """Rows that starts with #RES converts to a dict and later json"""
    items = row.split()
    tot[items[2]] = tot.get(items[2], {}) | {items[1]: items[3]}


def run(sie_file: Path):
    split_SIE(sie_file)


if __name__ == "__main__":
    # Interactive run
    run(Path("data/Bokföring - Bokio - 5592945496") / "5592945496_2023.se")
