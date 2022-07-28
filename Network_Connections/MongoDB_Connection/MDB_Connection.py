from pymongo import MongoClient
from datetime import datetime as dt
import random as rd
from pprint import pprint

class myMongoDB:
    
    def __init__(self, url='mongodb://localhost:27017/', dbName='DavidSampleDB',
                 collectName='SampleCollection0' ):
        # Attributes of connection
        self.mongoDbClientUrl    = url
        self.databaseName        = dbName
        self.collectionName      = collectName 

        # Connect to mongodb server
        self.client = MongoClient(self.mongoDbClientUrl)
        # Select database and collection
        self.databaseHandle = self.client[self.databaseName]
        self.collectionhandle = self.databaseHandle[self.collectionName]

    def SendPacket(self, newEntry=False):
        # Create data packet to send
        if newEntry == False:
            entry = {"DateTime": dt.now(), "RawData": str(10*rd.random())}
        else:
            entry=newEntry
        # Send new packet
        self.collectionhandle.insert_one(entry)

    def GetCollection(self, filter={}):
        docs = []
        for doc in self.collectionhandle.find(filter):
            print("======================================================")
            pprint(doc)
            docs.append(doc)
        return docs
    

# if __name__ == '__main__':
#     client  = myMongoDB()
#     client.SendPacket()
#     client.GetCollection()