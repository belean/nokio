import json
import sys
import re
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder


class Transaction(BaseModel):
    # org_nr: str
    date: date
    name: str
    description: Optional[str] = None
    recorded_at: datetime
    account: Dict[str, float]
    verificate: Optional[int] = None
    frozen: Optional[bool] = None


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
                tot["TRANS"][result.verificate] = result.model_dump(
                    exclude="verificate"
                ) | {"org_nr": tot["META"]["ORGNR"]}

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


def generate_general_ledger(content) -> pd.DataFrame:
    """Generate general ledger from list of transactions
    Args:
        content: Dict the content of transactions
    Returns pd.DataFrame accounts, transactions and values
    """
    mytrans = {}
    # trans_list = []
    # trans_index = []
    for key, val in content.get("TRANS").items():
        tmp = {}
        for key2, val2 in val.get("account").items():
            tmp[(int(key2[:-1]), key2[-1])] = val2
        mytrans[int(key)] = tmp
        # trans_list.append(val.get("account"))
        # trans_index.append(key)

    df = pd.DataFrame.from_records(mytrans).T
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["account", "side"])
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Transaction"
    return df


def get_GL_sum(df_gl):
    """Get the sum of all accounts"""
    return df_gl.sum()


def get_GL_transaction(df_gl, verificate_id: int) -> pd.DataFrame:
    return df_gl.loc[verificate_id, :].dropna()


def get_GL_accounts(df_gl, account_nr: int):
    return df_gl.loc[:, account_nr]


def get_IB(content) -> pd.DataFrame:
    """Get ingående balance (Saldo) from import at start of year 1 of Janurary
    Args:
        content, Json file with import from Bokio
    Raises:
    Returns pd.DataFrame with Saldo
    """
    index = []
    data = []
    for key, val in content.get("IB").items():
        """if float(val.get("0")) < 0:
            index.append((int(key), "K"))
            data.append(float(val.get("0")) * (-1))
        else:
            index.append((int(key), "D"))
            data.append(float(val.get("0")))"""
        index.append((int(key), "S"))
        data.append(float(val.get("0")))
    df = pd.DataFrame(data, index=index, columns=["IB"]).T
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["account", "side"])
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Saldo"
    return df


def current_saldo(content) -> pd.DataFrame:
    """Calculate the current saldo from sum of incoming balance and transactions

    Args:
        content (Json): From import file

    Raises:
        RuntimeError: _description_

    Returns:
        pd.DataFrame: with acconts
    """

    # incoming balance
    df_ib = get_IB(content)

    # General ledger
    df_gl = generate_general_ledger(content)

    df = pd.concat([df_ib, df_gl])  # .sum()
    df = df.reindex(sorted(df.columns), axis=1)

    # trans_id = (
    #    trans_id if trans_id is not None and trans_id <= df.index[-1] else df.index[-1]
    # )

    def get_df(account, df):
        if str(account)[0] not in ("2", "3"):
            return (
                df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            )
        else:
            return (
                df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            )

    df_saldo = df.T.groupby(level=0).apply(lambda df_g: get_df(df_g.name, df_g.T))

    return df_saldo


def any_saldo(content, accounts: list[int], trans_id: int = None):
    """_summary_

    Args:
        content (Json): From import file
        account (List[int]): Account numbers
        trans_id (int, optional): What transaction to include. Zero means incoming balance IB. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.DataFrame: with acconts
    """
    # incoming balance
    ib = get_IB(content)

    # General ledger
    df_gl = generate_general_ledger(content)

    df = pd.concat([ib, df_gl])  # .sum()
    df = df.reindex(sorted(df.columns), axis=1)

    trans_id = trans_id if trans_id is not None else sys.maxsize

    for account in accounts:
        # if all([(account, side) in df.columns for side in ("D", "K", "S")]):
        if trans_id == 0:
            return df.loc["IB", (account, "S")]
        elif 0 < trans_id < df.index[-1]:
            return (
                df.loc["IB", (account, "S")]
                + df.loc["IB":trans_id, (account, "D")].sum()
                - df.loc["IB":trans_id, (account, "K")].sum()
            )
        else:
            return current_saldo(content)[account]

    raise RuntimeError(f"Invalid transaction id: {trans_id}!")


def run(sie_file: Path):
    split_SIE(sie_file)


if __name__ == "__main__":
    # Interactive run
    run(Path("data/Bokföring - Bokio - 5592945496") / "5592945496_2023.se")
    generate_general_ledger(
        Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    )
