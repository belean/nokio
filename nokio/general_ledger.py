import json
from pathlib import Path
import pandas as pd
import numpy as np

# from nokio.bokio_import import get_IB, generate_general_ledger
from nokio.transaction import add_transactions, calculate_transaction_balance

"""General ledger is a module that manages the account list with start balance as well as all the 
registered transactions. It takes a list of transaction dicts and creates a pandas multi-index dataframe
"""


def calculate(df_gl: pd.DataFrame, brand: list = None):
    """Calculate the result after freezing the year"""
    gl_brand = {
        "asset": (1000, 1999),
        "dept": (2000, 2999),
        "income": (3000, 3999),
        "cost": (4000, 8999),
    }
    result = {}
    for k, a in gl_brand.items():
        tmp = []
        for c in df_gl.index:
            if a[0] <= c <= a[1]:
                tmp.append(c)
        result[k] = float(df_gl.loc[tmp].sum().round(2))
    return result


def generate_general_ledger(content: list[dict]) -> pd.DataFrame:
    """Generate general ledger from list of transactions
    Args:
        content: list of Dict, i.e. the content of transactions
    Returns pd.DataFrame accounts, transactions and values
    """
    mytrans = {}
    # trans_list = []
    # trans_index = []
    for trans_item in content:
        # for key, val in content.get("TRANS").items():
        tmp = {}
        for key, val in trans_item.get("t_data").items():
            tmp[(int(key[:-1]), key[-1])] = val
        mytrans[int(trans_item["t_id"])] = tmp
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


""" def current_saldo(content) -> pd.DataFrame:
    "Calculate the current saldo from sum of incoming balance and transactions

    Args:
        content (Json): From import file

    Raises:
        RuntimeError: _description_

    Returns:
        pd.DataFrame: with acconts
    "

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

    return df_saldo """


""" def any_saldo(content, accounts: list[int], trans_id: int = None):
    ""#_summary_

    Args:
        content (Json): From import file
        account (List[int]): Account numbers
        trans_id (int, optional): What transaction to include. Zero means incoming balance IB. Defaults to None.

    Raises:
        RuntimeError: _description_

    Returns:
        pd.DataFrame: with acconts
    ""#
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
"""


def run(content, new_content, content_jsonc):
    """df_ib + df_gl + df_new"""
    df_ib = get_IB(content)
    df_gl = generate_general_ledger(content)
    df_new = add_transactions(new_content)
    df_jsonc = add_transactions(content_jsonc)

    # Continue transaction Id in index
    df_new.index = pd.RangeIndex(df_gl.index[-1] + 1, df_gl.index[-1] + 1 + len(df_new))
    df_jsonc.index = pd.RangeIndex(
        df_new.index[-1] + 1, df_new.index[-1] + 1 + len(df_jsonc)
    )

    df = pd.concat([df_ib, df_gl, df_new, df_jsonc])
    df = df.reindex(sorted(df.columns), axis=1)
    if not abs(calculate_transaction_balance(df).sum().round(2)) < 0.49:
        raise RuntimeError("General ledger does not balance")

    def get_df(account, df):
        if str(account)[0] not in ("2", "3"):
            return (
                df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            )
        else:
            return (
                (-1) * df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            ) * (-1)

    return df.T.groupby(level=0).apply(lambda df_g: get_df(df_g.name, df_g.T))


if __name__ == "__main__":
    file_path = Path("data/Bokföring - Bokio - 5592945496/new_transactions.json")
    with open(file_path, "r") as fp:
        new_content = json.load(fp)

    file_path = Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    with open(file_path, "r") as fp:
        content = json.load(fp)

    run()
