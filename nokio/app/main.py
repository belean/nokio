import contextlib
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from nokio import settings
import pymongo

app = FastAPI()
uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWD}@{settings.MONGODB_DB}/?retryWrites=true&w=majority"

client = MongoClient(uri)
# db = client["Transaction"]
db = client.nokio


@app.get("/transactions")
def get_transactions(sort_by: str = "date", orgnr: str = None):
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

    query = {}
    if orgnr:
        query["Orgnr"] = orgnr

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
            },
        )
        .sort(sort_field, sort_order)
    )
    return list(transactions)
