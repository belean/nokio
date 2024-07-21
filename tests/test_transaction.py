import pytest
from bson.objectid import ObjectId
import json
from pathlib import Path
import pandas as pd
import numpy as np
from nokio.transaction import (
    db,
    recalc_GL,
    get_latest_transaction_gl,
    get_transactions_made_after_last_GL,
    add_transactions,
    open_jsonc,
    calculate_transaction_balance,
)
import dictdiffer

# TODO Fixture setting up and tearing down


@pytest.fixture
def setup():
    """Create a new GL with highest transaction +100"""
    gl = get_latest_transaction_gl()
    db["TransactionStore"].insert_one(
        {
            "Orgnr": "556997-9445",
            "Year": 2023,
            "GeneralLedger": {
                "Income": {"I_Income -|+ (3000)": 1000.0},
                "Cost": {"C_Post&Internet +|- (8265)": 0},
                "Dept": {"D_Eget kapital -|+ (2045)": -25000.0},
                "Asset": {"A_Kassa +|- (1930)": 0},
            },
            "last_transaction": int(gl["last_transaction"]) + 100,
        }
    )

    db["Transaction"].insert_one(
        {
            "t_id": int(gl["last_transaction"]) + 101,
            "t_name": "Domain fee 1Y",
            "t_date": "2023-10-03T16:38:12Z",
            "t_description": "Domain name to map host IP to nokio.org",
            "t_data": {
                "A_Kassa +/- (1930)": [0, 84.62],
                "C_Post&Internet +/- (8265)": [84.62, 0],
            },
            "t_method": "https://nokio.org/method/#Transaction_explained",
            "t_verification": 8,
        }
    )
    yield True
    db["TransactionStore"].delete_many(
        {"last_transaction": {"$gte": int(gl["last_transaction"]) + 100}}
    )
    db["Transaction"].delete_many({"t_id": {"$gte": int(gl["last_transaction"]) + 101}})


@pytest.fixture
def content():
    file_path = Path("data/Bokföring - Bokio - 5592945496/new_transactions.json")
    with open(file_path, "r") as fp:
        content = json.load(fp)
    return content


@pytest.fixture
def df(content):
    df_trans = pd.DataFrame().from_records(content)

    def split_account(d):
        tmp = {}
        for key, val in d.items():
            tmp[(int(key[:-1]), key[-1])] = val
        return tmp

    df_trans.account = df_trans.account.map(lambda d: split_account(d))

    df = pd.DataFrame().from_records(df_trans.account)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["account", "side"])
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Transaction"
    return df


def test_recalc_GL(setup):
    current_GL = get_latest_transaction_gl()
    assert (
        len(list(get_transactions_made_after_last_GL(current_GL))) >= 1
    ), "No transactions to apply"
    recalc_GL()
    result = get_latest_transaction_gl()
    diff_list = list(dictdiffer.diff(current_GL, result))
    assert diff_list[0][2] == [("C_Post&Internet +/- (8265)", 84.62)]
    assert diff_list[1][2] == [("A_Kassa +/- (1930)", -84.62)]
    assert diff_list[2][2][1] - diff_list[2][2][0] == 1


def test_add_transactions(content):
    result = add_transactions(content)
    assert (
        repr(result)
        == "account        2614  2641    2645     2890     4531   6910\nside              K     D       D        K        D      D\nTransaction                                               \n0               NaN  9.99     NaN    48.97      NaN  38.98\n1               NaN  9.29     NaN    45.70      NaN  36.41\n2               NaN  8.29     NaN    40.56      NaN  32.27\n3               NaN  8.69     NaN    42.54      NaN  34.85\n4               NaN  4.20     NaN    20.48      NaN  16.28\n5               NaN  4.03     NaN    19.65      NaN  15.62\n6            413.71   NaN  413.71  1654.83  1654.83    NaN\n7             28.15   NaN   28.15   112.58   112.58    NaN"
    )


def test_open_jsonc():
    file_path = Path(
        "/Users/backis/Desktop/Bokslut 2023/deklaration_2023/bokföring_sciple_2023.jsonc"
    )
    content = open_jsonc(file_path)
    result = add_transactions(content)
    assert (
        repr(result)
        == "account        1630            1930            2650          6992    8310\nside              D       K       D       K       D     K       D       K\nTransaction                                                              \n0              10.0     NaN     NaN     NaN     NaN  10.0     NaN     NaN\n1            6250.0  6250.0     NaN  6250.0     NaN   NaN  6250.0     NaN\n2            1017.0  1017.0     NaN  1017.0  1017.0   NaN     NaN     NaN\n3             155.0   155.0     NaN   155.0   155.0   NaN     NaN     NaN\n4               1.0     NaN     NaN     NaN     NaN   NaN     NaN    1.00\n5               1.0     NaN     NaN     NaN     NaN   NaN     NaN    1.00\n6               1.0     NaN     NaN     NaN     NaN   NaN     NaN    1.00\n7               NaN     NaN  540.97     NaN     NaN   NaN     NaN  540.97"
    )


def test_calculate_transaction_balance(df: pd.DataFrame):
    """Calculates the balance for each transaction and checks that the residual values is less than .49 sek

    Args:
        df (pd.DataFrame): containing the transactions
    """
    result = calculate_transaction_balance(df)
    assert abs(result.sum()) <= 0.49
