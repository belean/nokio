from pathlib import Path
import sys
import pandas as pd
import pymongo
import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# from bson.objectid import ObjectId
import json

from typing import TYPE_CHECKING
from nokio import settings

import logging

"""Transaction module handles the transactions including storage in MongoDB"""

logger = logging.getLogger(__name__)

# logging.basicConfig(level=logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter(
    "%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s"
)
stdout.setFormatter(fmt)
logger.addHandler(stdout)
logger.setLevel(logging.INFO)

uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWD}@{settings.MONGODB_DB}/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client: MongoClient = MongoClient(uri, server_api=ServerApi("1"))

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    logger.info("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    logger.error(e)

db = client.nokio


def get_transaction():
    return db["Transaction"].find_one({})


def get_transaction_store():
    return db["TransactionStore"].find_one()


def get_verificate():
    return db["Verificate"].find_one()  # TODO change name to Verification


def get_account_plan():
    return db["AccountPlan"].find_one()


result = get_transaction()
store_result = get_transaction_store()
verif_result = get_verificate()

logger.debug(result["t_name"])
logger.debug(store_result["GeneralLedger"])
logger.debug(verif_result["v_image"])
logger.debug(get_account_plan()["1630"])

# Common account map
account_map = {
    "A_": "Asset",
    "D_": "Dept",
    "I_": "Income",
    "C_": "Cost",
}


def get_next_transaction_id(orgnr: str):
    """Returns the greatest transaction id available. The ids are never reused
    and unique per org.
    """
    return (
        db["Transaction"]
        .find({"Orgnr": orgnr})
        .sort("t_id", pymongo.DESCENDING)
        .limit(1)
    )


def get_latest_transaction_gl(org: int):
    """Find the general ledger with the highest transaction number"""
    # Get the latest of GL by transaction id
    return db["TransactionStore"].find({"Orgnr": org}).limit(1)


def get_transactions_made_after_last_GL(current_GL: dict):
    """Get transactions greater then last transaction id"""

    return db["Transaction"].find({"t_id": {"$gt": current_GL["last_transaction"]}})


def recalc_GL():
    """Get a list of valid transaction and recalculate the GL"""

    current_GL = get_latest_transaction_gl()
    logger.info(f"current_GL: {current_GL}")

    transactions = get_transactions_made_after_last_GL(current_GL)
    logger.info(f"transactions: {transactions}")

    for transaction in transactions:
        logger.info(transaction["t_name"])

        # Get Debit & Kredit from transaction
        logger.info(transaction["t_data"])
        for key, value in transaction["t_data"].items():
            logger.info(f"{key}: {value[0]-value[1]}")
            account_group = account_map[key[:2]]

            # Create if it does not exist already
            current_GL["GeneralLedger"][account_group][key] = (
                current_GL["GeneralLedger"][account_group].get(key, 0)
                + value[0]
                - value[1]
            )

        current_GL["last_transaction"] = transaction["t_id"]

        logger.info(current_GL)
        oid = current_GL.pop("_id")
        db["TransactionStore"].update_one({"_id": oid}, {"$set": current_GL})


def reserve_transactions(org: str, last_added_id: int = None):
    if last_added_id > 0:
        result = db["TransactionStore"].update_one(
            {"Orgnr": org}, {"$set": {"last_transaction_seen": last_added_id}}
        )
    else:
        result = db["TransactionStore"].update_one(
            {"Orgnr": org}, {"$inc": {"last_transaction_seen": 50}}
        )
    return result.acknowledged


def add_transactions(content: list) -> int:
    """Add transactions to the data store

    Args:
        content (list): List of new transactions (even one)

    Raises: RuntimeError when transactions are unbalanced (Kredit - Debit) with an
            combined error of more than 0.49 SEK

    Returns:
        int, the latest id added
    """

    # VAlidate the content

    # get the last transaction id from data store
    org = content["META"]["ORGNR"]
    get_latest_transaction_gl(org)
    get_next_transaction_id(org)

    # reserve 50 ids at a time
    if reserve_transactions(org):
        for idx, item in enumerate(content["TRANS"].items()):
            db["Transaction"].insert_many()
            ...
        else:
            reserve_transactions(org, idx + 1)
    return 0

    """
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
    # Make sure the transaction balance otherwise throw error in content
    balance = calculate_transaction_balance(df)
    if abs(balance.sum()) > 0.49:
        logger.error(f"Unbalanced transactions: {balance}")
        raise RuntimeError("The list of transactions are not balanced")
    return df
    """


def calculate_transaction_balance(df: pd.DataFrame):
    """Takes a multiindex dataframe and per transaction check that both sides balances

    Args:
        df (pd.DataFrame): Transactions
    Raises:
    Returns: List of balance
    """

    def get_df(side):
        return side["D"] - side["K"]

    return df.T.groupby(level=1).sum().apply(lambda x: get_df(x))


def run():
    recalc_GL()


if __name__ == "__main__":
    run()
