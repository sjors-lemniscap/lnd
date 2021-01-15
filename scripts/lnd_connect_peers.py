#!/usr/bin/env python3

import requests, subprocess, json, sys, os, logging, shutil, glob

log_file="/data/custom/connect_peers.log"

logging.basicConfig(filename=log_file,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger("urllib3").setLevel(logging.WARNING)

devnull = open(os.devnull, 'wb')
urls = [ 'https://1ml.com/node?order=capacity&json=true',  
         'https://1ml.com/node?order=lastupdated&json=true', 
         'https://1ml.com/node?order=mostchannels&json=true',
         'https://1ml.com/node?order=newest&json=true',
         'https://1ml.com/node?order=capacitychange&json=true',
         'https://1ml.com/node?order=channelcount&json=true',
         'https://1ml.com/node?order=channelcountchange&json=true',
         'https://1ml.com/node?order=nodeconnectednodecount&json=true']

peerCommand = "/data/umbrel/bin/lncli listpeers"
process     = subprocess.Popen(peerCommand.split(), stdout=subprocess.PIPE)
peers       = json.loads(process.communicate()[0])
pub_keys    = []

for peer in peers["peers"]:
    pub_keys.append(peer["pub_key"])


# Parse json from urls
logging.info("Get new peers from 8 url")

for url in urls:
    resp = requests.get(url)
    data = resp.json()
    ok_count = 0
    error_count = 0
    already_count = 0
    for line in data:
        if len(line["addresses"]) != 0:
            if line["pub_key"] not in pub_keys:
                bashCommand = "timeout 5 /data/umbrel/bin/lncli connect %s@%s" % ( line["pub_key"], 
                                                                  line["addresses"][0]["addr"] 
                                                                )
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=devnull)
                streamdata = process.communicate()[0]
                if process.returncode == 0:
                    ok_count += 1
                else:
                    error_count += 1
            else:
                already_count += 1
                continue
        else:
            continue
logging.info("%s peer(s) already connected" % already_count)
logging.info("%s peer(s) newly connected" % ok_count)
logging.info("%s peer(s) with an error" % error_count)
logging.info("Retrieved all peers")

# Cleanup /tmp/ folder
for f in glob.glob("/tmp/_MEI*/"):
    shutil.rmtree(f)