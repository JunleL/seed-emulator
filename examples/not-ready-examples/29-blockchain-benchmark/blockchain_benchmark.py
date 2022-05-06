#!/usr/bin/env python3
# encoding: utf-8

from seedemu import *
from seedemu.services.EthereumService import ConsensusMechanism
from test_tiny_net import createTestNet
from os import mkdir, chdir, getcwd, path

emu = Emulator()

# Create the Ethereum layer
# saveState=True: will set the blockchain folder using `volumes`,
# manual: requires you to trigger the /tmp/run.sh bash files in each container to lunch the ethereum nodes
# so the blockchain data will be preserved when containers are deleted.
# Note: right now we need to manually create the folder for each node (see README.md). 
eth = EthereumService(saveState = True, manual=False)

eth.setBaseConsensusMechanism(ConsensusMechanism.POA)

# Create Ethereum nodes (nodes in this layer are virtual)
ethereum_node_count=200
sealers=[]
bootnodes=[]
hport=8544
cport=8549
output = './output'

# Currently the minimum amount to have to be a validator in proof of stake
balance = 32 * pow(10, 8)

all_eth_node_index = [i for i in range(1, ethereum_node_count+1)]

# Setting a third of nodes as bootnodes
for i in all_eth_node_index:
    e = eth.install("eth{}".format(i))
    e.__class__= EthereumServer
    if i%3 == 0:
        e.setBootNode(True)
        bootnodes.append(i)
    else:
        # e.createPrefundedAccounts(balance, 1)
        e.createPrefundedAccounts(balance= balance, number= 1, password= "admin", saveDirectory = "/home/seed/Desktop/ben-emu/examples/not-ready-examples/blockchain-benchmark/keystore")
        e.unlockAccounts().startMiner() 
        sealers.append(i)
    
    e.enableExternalConnection() # not recommended for sealers in production mode
    emu.getVirtualNode('eth{}'.format(i)).setDisplayName('Ethereum-poa-{}'.format(i)).addPortForwarding(hport, cport)
    hport = hport + 1

print("There are {} sealers and {} bootnodes".format(len(sealers), len(bootnodes)))
print("Sealers {}".format(sealers))
print("Bootnodes {}".format(bootnodes))

# Add the layer and save the component to a file
emu.addLayer(eth)
# emu.dump('component-blockchain-benchmark.bin')


emu_tiny_net = Emulator()
emu_tiny_net = createTestNet(numberOfAs = ethereum_node_count)

emu_merge = emu_tiny_net.merge(emu)

for i in all_eth_node_index:
    emu_merge.addBinding(Binding('eth{}'.format(i), filter=Filter(asn = 30+i,nodeName="host0")))

def createDirectoryAtBase(base:str, directory:str, override:bool = False):
    cur = getcwd()
    if path.exists(base):
        chdir(base)
        if override:
            rmtree(directory)
        mkdir(directory)
    chdir(cur)


saveState = True
def updateEthStates():
    if saveState:
        createDirectoryAtBase(output, "eth-states/")
        for i in all_eth_node_index:
            createDirectoryAtBase(output, "eth-states/" + str(i))

emu_merge.render()

# Generate the Docker files
emu_merge.compile(Docker(), output)
updateEthStates()

# !cd output
# !dcbuild
# !ls | grep -Ev '.yml$|^dummies$|^morris|^z_start' | xargs -n10 -exec docker-compose up -d
