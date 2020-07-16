import json
import random
import configparser
from locust import HttpUser, TaskSet, between, task

cfgParser = configparser.ConfigParser()
cfgParser.read("testConfig.ini")

blocksUpperLimit = int(cfgParser["testConfig"]["blocksSynced"])
sessionKey = str(cfgParser["testConfig"]["sessionKey"])

class TxByTxIdApiUser(HttpUser):
    wait_time = between(2, 5)

    # user fetches a random block by height, uses the block hash to fetch all txns from that block
    def on_start(self):
        response = self.client.get(
            url = "/v1/block/height/" + str(random.randint(1, blocksUpperLimit)),
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
    @task
    def getTxsByTxIds(self):
        while(len(self.txids) != 0):
            self.client.get(
                url = "/v1/transaction/" + self.txids.pop(),
                headers = {"authorization": "Bearer " + sessionKey},
                verify = False
            )
