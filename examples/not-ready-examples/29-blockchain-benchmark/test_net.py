#!/usr/bin/env python3
# encoding: utf-8

from seedemu import *

emu = Emulator()
base = Base()
ebgp = Ebgp()

asn_list = [99,100,101] # 100 conflict with ix100 below

# Create Internet exchange
ix100 = base.createInternetExchange(100)
ix100.getPeeringLan().setDisplayName("New York-100")


for asn in asn_list:
    Makers.makeStubAs(emu, base, asn, 100,[None,None])

ebgp.addRsPeers(100,asn_list)

emu.addLayer(base)
emu.addLayer(Routing())
emu.addLayer(ebgp)
emu.addLayer(Ibgp())
emu.addLayer(Ospf())

emu.render()

emu.compile(Docker(), './output')


