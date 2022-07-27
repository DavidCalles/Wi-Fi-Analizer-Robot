import pymongo
from pymongo import MongoClient
from datetime import datetime as dt


mongoDbClientUrl    = 'mongodb://localhost:27017/'
databaseName        = 'DavidSampleDB'
collectionName      = 'SampleCollection0'  

# Connect to mongodb server
client = MongoClient(mongoDbClientUrl)

# Select database and collection
databaseHandle = client[databaseName]

collectionhandle = databaseHandle[collectionName]

# Create data packet to send
newEntry = {"_id": str(1), "DateTime": dt.now(), "RawData": str(12.5)}