#!/usr/bin/env python3

import gc
import json
import pyjq
import datetime
# urllib.request module uses HTTP/1.1 and includes Connection:close header in its HTTP requests
import urllib.request
# this makes it easier to avoid errors when the requested json element is not present
from dictor import dictor

# You will likely need to install these modules
# pip3 install websocket-client
# pip3 install pyjq (requires "apt install autoconf libtool" on Bionic)
# pip3 install dictor

# Define these to your needs
# get the proper string for your validator from stargazer.certus.one/validators
# or from your priv_validator_key.json file
yourval = "<your-validator-id>"
# To test this enter below a validator that has been missing blocks frequently
# and uncomment the line
#yourval = "<flaky-validator-id>"
# When a lot of validators miss a block, it is not your fault. if you alone or only a handful missed,
# you should look into your setup. Set alertIfLessThan to the max number of validators missing a block you'd tolerate
# before you'd want to be alerted. If you set it to 0, you will never get an alert.
alertIfLessThan = 5
baseurl = "http://localhost:26657/block?height="
logfile = "cosmosvalmon.log"

# Output to stdout is
# "block height, proposer ID, number of validators that missed the block"
# If your val missed the block, it appends "(including your validator)."
# If the number of validators that missed is below your threshold (alertIfLessThan)
# it will further append "X validators missed, below your threshold of Y"

# No need to change anything from here on
headers = {'content-type': 'application/json'}

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header = (headers)
    response = urllib.request.urlopen(req)
    data = response.read()
    datajson = json.loads(data)
    return datajson

from websocket import create_connection
ws = create_connection("ws://localhost:26657/websocket")
ws.send(json.dumps({"jsonrpc": "2.0", "method": "subscribe",
                    "id": "1", "params": {"query": "tm.event='NewBlock'"}}))

try:
    while True:
        blockdata = ws.recv()
        blockjson = json.loads(blockdata)
        block = str(dictor(blockjson, 'result.data.value.block.header.height'))
        if block != "None":

            block = int(block)
            alert = ""
            yourvalmissed = ""
            now = datetime.datetime.now()

            # starting with the previous block, to look into the current block
            # and count how many validators missed it.
            # so this tool is always "one block behind"
            previousblock = block - 1
            url = baseurl + str(previousblock)
            result = fetch_json(url)
            # jq -r '.result.block.header.proposer_address'
            proposer_address = (
                dictor(result, 'result.block.header.proposer_address'))

            url = baseurl + str(block)
            # jq -r '.result.block.last_commit.precommits[].validator_address'
            result = fetch_json(url)
            validator_addresses = (
                pyjq.all('.result.block.last_commit.signatures[].validator_address', result))

            # Start out with the assumption that your val did miss the block
            missed = 1
            # and count the number of validators that missed it starting from 0
            valmissedcount = 0
            # here you append the address of each validator that missed the block
            valset = ""

            # See if you missed the block, count how many validators missed, add them to a list
            for i in validator_addresses:
                if i == yourval:
                    missed = 0
                    valset = valset + str(i) + ","
                elif i is None:
                    valmissedcount = valmissedcount + 1
                else:
                    valset = valset + str(i) + ","

            if missed == 1:
                yourvalmissed = ", (including your validator)."

                if valmissedcount < alertIfLessThan:
                        alert = " Also sending an alert: " + str(valmissedcount) + " validators missed - below your threshold of " + str(alertIfLessThan)

                log = (now.strftime("%Y-%m-%d-%H:%M:%S") + ', ' + str(previousblock) + ', ' + proposer_address + ', ' + str(valmissedcount) + yourvalmissed)
                # write to log file
                with open(logfile, 'a+') as f:
                    f.write(log + alert + '\n')

            print (str(previousblock) + ', ' + proposer_address + ', ' + str(valmissedcount) + yourvalmissed + alert, flush=True)

            if alert != "":
                print(log)
                print(alert)
            
            gc.collect()

except KeyboardInterrupt:
    print('............Exiting!')
