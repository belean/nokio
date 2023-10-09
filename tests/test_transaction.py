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


def reset():
    db["TransactionStore"].update_one(
        {"_id": ObjectId("65227b7a36de85a4fd454dd6")},
        {
            "$set": {
                "556997-9445": 2023,
                "GeneralLedger": {
                    "Income": {"I_Income -|+ (3000)": 1000.0},
                    "Cost": {"C_Post&Internet +|- (8265)": 84.62},
                    "Dept": {"D_Eget kapital -|+ (2045)": -25000.0},
                    "Asset": {"A_Kassa +|- (1930)": 25915.38},
                },
                "last_transaction": 3,
            }
        },
    )


def test_recalc_GL():
    current_GL = get_latest_transaction_gl()
    assert (
        len(list(get_transactions_made_after_last_GL(current_GL))) >= 1
    ), "No transactions to apply"
    recalc_GL()
    result = get_latest_transaction_gl()
    diff_list = list(dictdiffer.diff(current_GL, result))
    assert diff_list[0][2] == (84.62, 169.24)
    assert diff_list[1][2] == (25915.38, 25830.760000000002)
    assert diff_list[2][2] == (3, 4)
