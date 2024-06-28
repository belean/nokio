import json
import re
import pandas as pd
from pathlib import Path


def split_SIE(sie_file: Path):
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
                tot["TRANS"][result.pop("verificate")] = result

    with open(
        "data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json",
        "w",
        encoding="utf-8",
    ) as fj:
        json.dump(tot, fj, ensure_ascii=False, indent=2)


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
            result["date"] = meta_data[2]
            result["name"] = meta_data[3]
            result["recorded_at"] = meta_data[4]
            print(idx, "ver")
        elif line[:1] == "{":
            is_active = True
            print(idx, "start")
        elif line[:1] == "}":
            is_active = False
            print(idx, "stop")
        elif is_active:
            l_line: list = line.strip().split()
            account[l_line[1]] = l_line[3]
    result["account"] = account
    return result


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


def generate_general_ledger(content) -> pd.DataFrame:
    """Generate general ledger from list of transactions
    Args:
        content: Dict the content of transactions
    Returns pd.DataFrame accounts, transactions and values
    """

    trans_list = []
    trans_index = []
    for key, val in content.get("TRANS").items():
        trans_list.append(val.get("account"))
        trans_index.append(key)
    return pd.DataFrame.from_records(trans_list, index=trans_index)


def get_GL_sum(df_gl):
    """Get the sum of all accounts"""
    return df_gl.astype(float).sum()


def get_GL_transaction(df_gl, verificate_id: str) -> pd.DataFrame:
    return df_gl.astype(float).loc[verificate_id, :].dropna()


def get_GL_accounts(df_gl, account_nr: str):
    return df_gl.astype(float).loc[:, account_nr]


def get_IB(content) -> pd.DataFrame:
    """Get ingående balance from list of transactions"""
    index = []
    data = []
    for key, val in content.get("IB").items():
        index.append(key)
        data.append(val.get("0"))
    return pd.DataFrame(data, index=index, columns=["IB2023"])


def current_saldo(content):
    """Calculate the current saldo from sum of incoming balance and transactions"""
    # incoming balance
    ib = get_IB(content)

    # General ledger
    df_gl = generate_general_ledger(content)

    return pd.concat([ib.T.astype(float), df_gl.astype(float)]).sum()


def run(sie_file: Path):
    split_SIE(sie_file)


if __name__ == "__main__":
    # Interactive run
    run(Path("data/Bokföring - Bokio - 5592945496") / "5592945496_2023.se")
    generate_general_ledger(
        Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    )
