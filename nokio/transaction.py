from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from typing import TYPE_CHECKING

uri = "mongodb+srv://nokio_user:YJGZKWjs3qo85RFT@cluster0.0euea7i.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client:MongoClient = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
