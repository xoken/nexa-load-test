import json
import random
import urllib3
import requests
import configparser
from locust import HttpUser, TaskSet, between, task

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cfgParser = configparser.ConfigParser()
cfgParser.read("testConfig.ini")

host = str(cfgParser["testConfig"]["host"])
sessionKey = str(cfgParser["testConfig"]["sessionKey"])
blocksLowerLimit = int(cfgParser["testConfig"]["blocksLowerLimit"])

blocksSynced = int(json.loads(requests.get(
    url = host + "/v1/chain/info",
    headers = {"authorization": "Bearer " + sessionKey},
    verify = False
).text)["chainInfo"]["blocksSynced"])

print("Got chain work info from node, blocks synced: " + str(blocksSynced))

def getRandomBlock():
    return str(random.randint(blocksLowerLimit, blocksSynced))

class TxByTxIdApiUser(HttpUser):
    wait_time = between(2, 5)

    # user fetches a random block by height, uses the block hash to fetch all txns from that block
    def on_start(self):
        response = self.client.get(
            url = "/v1/block/height/" + getRandomBlock(),
            name = "/v1/block/height/...",
            headers = {"authorization": "Bearer " + sessionKey},
            verify = False
        )
        responseObject = json.loads(response.text)
        self.blockHash = responseObject["block"]["hash"]
        response = self.client.get(
            url = "/v1/block/txids/" + responseObject["block"]["hash"],
            name = "/v1/block/txids/...",
            headers = {"authorization": "Bearer " + sessionKey},
            verify = False
        )
        responseObject = json.loads(response.text)
        self.txids = responseObject["txids"]

    # user queries all transactions from the block by txid
    # then, queries all outputs by outputAddress parsed from the transactions
    @task
    def getTxsByTxIds(self):
        while(len(self.txids) != 0):
            response = self.client.get(
                url = "/v1/transaction/" + self.txids.pop(),
                name = "/v1/transaction/...",
                headers = {"authorization": "Bearer " + sessionKey},
                verify = False
            )
            for output in json.loads(response.text)["tx"]["tx"]["txOuts"]:
                self.client.get(
                    url = "/v1/address/" + output["address"] + "/outputs",
                    name = "/v1/address...",
                    headers = {"authorization": "Bearer " + sessionKey},
                    verify = False
                )
