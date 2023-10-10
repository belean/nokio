import pytest
from bson.objectid import ObjectId
from nokio.transaction import (
    db,
    recalc_GL,
    get_latest_transaction_gl,
    get_transactions_made_after_last_GL,
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
