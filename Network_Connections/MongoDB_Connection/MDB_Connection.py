from pymongo import MongoClient
from datetime import datetime as dt
import random as rd
from pprint import pprint
from gridfs import GridFS
from bson import Binary
from pickle import dumps

class myMongoDB:
    
    def __init__(self, url='mongodb://localhost:27017/', dbName='DavidSampleDB',
                 collectName='SampleCollection0' ):
        # Attributes of connection
        self.mongoDbClientUrl    = url
        self.databaseName        = dbName
        self.collectionName      = collectName 
        self.DocNameIndex        = 0

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
    
    def SendImage(self, imgPath):
        #Create an object of GridFs for the above database.
        fs = GridFS(self.databaseHandle)

        #Open the image in read-only format.
        with open(imgPath, 'rb') as f:
            contents = f.read()

        #Now store/put the image via GridFs object.
        filename = f"RobotImage{self.DocNameIndex}"
        fs.put(contents, filename=filename)
    
    def AddImageBinary(self, imgPath, collection, field="img0"):
        #Open the image in read-only format.
        with open(imgPath, 'rb') as f:
            contents = f.read()
        collection[field] = Binary(dumps(contents))

    def GetCollection(self, filter={}):
        docs = []
        for doc in self.collectionhandle.find(filter):
            print("======================================================")
            pprint(doc)
            docs.append(doc)
        return docs
    
    def GetCollectionNoPrint(self, filter={}):
        return self.collectionhandle.find(filter)
    
    # def KeepOnlyNewerSamples(self, keepLast=10):
    #     allDocs = self.collectionhandle.find({})
    #     if (len(allDocs) > keepLast):
    #         # We need to delete
    #     else:
    #         return len(allDocs)   
     
    def DeleteAll(self):
        print("Deleting all documents")
        self.collectionhandle.delete_many({})
    
    def DeleteOlder(self, minutes=10):
        for records in self.collectionhandle.find():
            #print(records.get('TimeStamp'))
            if int(dt.now().timestamp()) - minutes*60 > records.get('TimeStamp'):
                print(self.collectionhandle.delete_one({'TimeStamp' : records.get('TimeStamp')}))

# if __name__ == '__main__':
#     client  = myMongoDB()
#     client.SendPacket()
#     client.GetCollection()