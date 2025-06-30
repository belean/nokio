import contextlib
import sys
from fastapi import FastAPI, HTTPException, Query, Request, Body, status
from pydantic import BaseModel, Field
from pydantic.types import Json
from pymongo import MongoClient
from bson import ObjectId, json_util
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from nokio.transaction import get_next_transaction_id
from nokio import settings
import pymongo
import json
from datetime import datetime
import logging
import uvicorn
import re


from typing import Optional, Any

logging.basicConfig(level=logging.DEBUG)  # TODO soething nicer like


class t_data(BaseModel):
    account: str
    value: float


class TransactionModel(BaseModel):
    # t_id: int
    t_name: str
    t_date: str
    t_data: str  # dict[str, float]
    t_locked: Optional[bool] = None
    # Orgnr: str
    t_description: Optional[str] = None
    t_verification: Optional[str] = None
    # customField1: float | None
    # savTemplate: bool | None


class UpdateTransactionModel(BaseModel):
    t_name: Optional[str]
    t_date: Optional[str] = None
    t_data: Json[Any] = Field(default_factory=dict)
    t_locked: Optional[bool] = None
    Orgnr: Optional[str] = None
    t_description: Optional[str] = None
    t_verification: Optional[str] = None


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = FastAPI()
uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWD}@{settings.MONGODB_DB}/?retryWrites=true&w=majority"

client = MongoClient(uri)
# db = client["Transaction"]
db = client.nokio


@app.get("/transaction")
def get_transaction_list(orgnr: str, year: str, sort_by: str = "date"):
    """Get a list of tranactions sorted by date

    Args:
        sort_by (str, optional): list Sorted by str. Defaults to 'date'.
    """

    if sort_by == "date":
        sort_field = "t_date"
        sort_order = pymongo.DESCENDING
    elif sort_by == "id":
        sort_field = "t_date"
        sort_order = pymongo.DESCENDING
    else:
        sort_field = "t_name"
        sort_order = pymongo.ASCENDING

    query = {"Orgnr": orgnr, "t_date": re.compile(year)}
    # if orgnr:
    #    # Convert string to dict
    #    query["Orgnr"] = json.loads(orgnr)["orgnr"]

    transactions = (
        db["Transaction"]
        .find(
            query,
            {
                "t_id": 1,
                "t_name": 1,
                "t_date": 1,
                "t_description": 1,
                "Orgnr": 1,
                "_id": 0,
                "t_data": 1,
                "t_locked": 1,
            },
        )
        .sort(sort_field, sort_order)
    )
    return list(transactions)


@app.get("/transaction/{trans_id}")
def show_trans(trans_id: str, orgnr: str):
    query = {"t_id": int(trans_id), "Orgnr": orgnr}

    if (transaction := db["Transaction"].find_one(query, {"_id": 0})) is not None:
        return transaction

    raise HTTPException(status_code=404, detail=f"Transaction: {trans_id} not found!")


@app.put("/transaction/{trans_id}", response_description="Update a transaction")
def update_trans(
    trans_id: str,
    orgnr: str,
    request: Request,
    transaction: UpdateTransactionModel = Body(...),
):
    logging.debug(f"1.{transaction=}")
    transaction = {k: v for k, v in transaction.model_dump().items() if v is not None}
    logging.debug(f"2.{transaction=}")
    query = {"t_id": int(trans_id), "Orgnr": orgnr}

    if len(transaction) >= 1:
        logging.debug("Len >=1")
        update_result = db["Transaction"].update_one(query, {"$set": transaction})
        logging.debug(f"{update_result=}")
        if update_result.modified_count == 1:
            logging.debug(f"{update_result.modified_count=}")
            if (
                updated_task := MongoJSONEncoder().encode(
                    db["Transaction"].find_one(query)
                )
            ) is not None:
                return updated_task
    if (
        existing_task := MongoJSONEncoder().encode(
            db["Transaction"].find_one({"t_id": int(trans_id)})
        )
    ) is not None:
        logging.debug(f"{existing_task=}")
        return existing_task

    raise HTTPException(status_code=404, detail=f"Transaction {trans_id} not found")


@app.post("/transaction", response_description="Add new transaction")
def create_transaction(orgnr: str, transaction: TransactionModel = Body(...)):
    transaction = jsonable_encoder(transaction)
    try:
        transaction["t_id"] = next(get_next_transaction_id(orgnr))["t_id"] + 1
    except StopIteration:
        # No existing transaction for orgnr
        transaction["t_id"] = 1
    transaction["Orgnr"] = orgnr
    transaction["t_data"] = json.loads(transaction["t_data"])
    new_transaction = db["Transaction"].insert_one(transaction)
    # transaction.model_dump_json
    # transaction_dict = transaction.model_dump()
    # if (transaction :=
    # result = db["Transaction"].insert_one(transaction.model_dump)
    # return transaction
    # raise HTTPException(
    #     status_code=404,
    #     detail=f"Transaction: could not be created!\n Provided data: {transaction_dict}",
    # )
    created_transaction = MongoJSONEncoder().encode(
        db["Transaction"].find_one({"_id": new_transaction.inserted_id})
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_transaction
    )


@app.get("/template")
def template():
    return [
        {
            "t_name": "Salary",
            "t_data": {"3000K": 0.0, "1930D": 0.0, "2640D": 0.0},
            "share": True,
        },
        {
            "t_name": "Domain fee",
            "t_data": {"1930K": 0.0, "8265D": 0.0},
            "share": False,
        },
    ]

    raise HTTPException(status_code=404, detail=f"Transaction: {templ_id} not found!")


@app.get("/user/{org_email}")
def get_user(org_email: str) -> list:
    """Gets companies connected to logged in users email. It can be 1 or more companies
    Args:
        org_email: str the loggd in user email
    Raises:
        HTTPException
    Returns:
        List of companies with orgid and name"""
    if (
        org := db["user"].find(
            {"$or": [{"org_email": org_email}, {"org_link": org_email}]}, {"_id": 0}
        )
    ) is not None:
        my_orgs = list(org)
        return [{"orgnr": org["orgnr"], "orgname": org["org_name"]} for org in my_orgs]

    raise HTTPException(status_code=404, detail=f"User: {org_email} not found!")


@app.get("/accounts")
def get_accounts(orgnr: str):
    """Get a list of accounts to consolidate
    Returns a list of accounts with their names and value by consolidationDate"""
    if not orgnr:
        raise HTTPException(status_code=400, detail="orgnr is required")

    accounts = db["AccountPlan"].find_one({"Orgnr": orgnr}, {"_id": 0, "Orgnr": 0})
    if accounts is None:
        raise HTTPException(status_code=404, detail=f"Accounts for {orgnr} not found")

    # get the latest consolidation date
    latest_consolidation = list(
        db["Consolidate"]
        .find({"Orgnr": orgnr}, {"_id": 0, "Orgnr": 0, "recorded_at": 0})
        .sort("consolidationDate", pymongo.DESCENDING)
        .limit(1)
    )[0]

    return {
        f"{k} - {v[0]}": latest_consolidation.get(k, 0) for k, v in accounts.items()
    } | {
        "consolidationDate": latest_consolidation.get(
            "consolidationDate", "Not consolidated yet"
        )
    }


@app.post("/consolidate")
def consolidate_accounts(orgnr: str, accounts: dict):
    """Consolidate accounts by summing up the values of each account"""
    if not orgnr:
        raise HTTPException(status_code=400, detail="orgnr is required")
    if not accounts:
        raise HTTPException(status_code=400, detail="accounts are required")

    # Convert string keys to integers
    accounts = {k.split(" - ")[0]: v for k, v in accounts.items()}

    # Update the database with the consolidated values
    accounts["recorded_at"] = datetime.now().isoformat()
    accounts["Orgnr"] = orgnr
    result = db["Consolidate"].insert_one(accounts)

    if result.acknowledged == False:
        logging.error(f"Failed to consolidate accounts for {orgnr}")
        raise HTTPException(status_code=404, detail=f"Accounts for {orgnr} not found")

    return {"message": "Accounts consolidated successfully"}


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
