
import pandas as pd
import json
from datetime import datetime
import boto3
import botocore
import asyncio
import uuid
from threading import Lock
from pymongo import MongoClient

DEFAULT_LAMBDA_SIZE = 5
LAMBDA_SUFFIX_IDENTIFIER = "LambdaService"

class lambdaService:

    _instance = None

    currentLambdas = []

    lambdaConfiguration = botocore.config.Config(
        read_timeout=900,
        connect_timeout=900,
        max_pool_connections = 50,
        retries={"max_attempts": 5}
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(lambdaService, cls).__new__(cls)
            # Put any initialization here.
        
        return cls._instance
    
    def __init__(self):
        print("Initializing Lambda Service ....")
        self.generateLambdaList(DEFAULT_LAMBDA_SIZE, "StackedTrends", LAMBDA_SUFFIX_IDENTIFIER)
        print("Completed Lambda Server Initialization")

    def start(self):
        print("Initializing Lambda - Default Bank")


    def createLambdaFunctionAWS(self, functionName: str, queryType):
        
        awsLambdaClient = boto3.client('lambda')
        
       # awsLambdaClient.create_function(
       #     Role='arn:aws:iam::680428038157:role/gtrends',
       #     FunctionName=functionName,
       #     Runtime= 'python3.8',
       #     Handler='lambda_function.lambda_handler',
       #     Code= {'S3Bucket':'gtrends-lambdas', 'S3Key': queryType + '.zip'},
       #     Timeout=900,
       # )

        return {
                "functionName" : functionName, 
                "creationDate" : datetime.utcnow(), 
                "server" : "default", # this is used later to load balance lambdas across multiple apis
                "executionCount" : 0,
                "expired" : False 
                }

    def loadActiveLambdas(self):

        mongoClient = MongoClient("localhost:47017")
        mongoDatabase = mongoClient["LelexPrimeConfig"]
        lambdasCollection = mongoDatabase["lambdas"]

        lambdasCollection = [term for term in lambdasCollection.find({ "expired": False })]

        return lambdasCollection

    def deleteLambdaFunctionAWS(self, functionName: str):
        try:
            self.awsLambdaClient.delete_function(
                FunctionName=functionName
            )
        except:
            print(f"issues deleting lambda {functionName} befure it does not exist")

    def saveLambdasToMongo(self, lambdaItem: json):

        mongoClient = MongoClient("localhost:47017")
        mongoDatabase = mongoClient["LelexPrimeConfig"]
        lambdasCollection = mongoDatabase["lambdas"]

        #for item in lambdaItems:
        lambdasCollection.insert(lambdaItem)

       # lambdasCollection.insert_many(lambdaItems)
        

    async def createLambdaFunction(self, functionName: str, queryType: str):

        awsLambdaClient = boto3.client('lambda')

        try: 
            self.createLambdaFunctionAWS(functionName, queryType, awsLambdaClient)
        except:
            self.deleteLambdaFunctionAWS(functionName, awsLambdaClient)
            self.createLambdaFunctionAWS(functionName, queryType, awsLambdaClient)

    def generateLambdaList(self, numLambdas: int, queryType: str, identifier: str):
    
        lambdaListGenerated = self.loadActiveLambdas()
        print(lambdaListGenerated)
        totalLambdasToCreate = numLambdas - len(lambdaListGenerated)

        for index in range(0, totalLambdasToCreate):
            uniqueLambdaKey = str(uuid.uuid4()).replace("-","")
            lambdaName = "{queryType}-{index}-{identifier}".format(queryType = queryType, index = uniqueLambdaKey, identifier=identifier)
            print(lambdaName)
            lambdaItem = self.createLambdaFunctionAWS(lambdaName, queryType)
            self.saveLambdasToMongo(lambdaItem)
            lambdaListGenerated.append(lambdaItem)
        
        #self.saveLambdasToMongo(lambdaListGenerated)

        return lambdaListGenerated
