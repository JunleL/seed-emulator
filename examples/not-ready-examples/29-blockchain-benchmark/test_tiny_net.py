#!/usr/bin/env python3
# encoding: utf-8

from seedemu import *

def createTestNet(numberOfAs= 20, isRender = False):
    emu = Emulator()
    base = Base()
    ebgp = Ebgp()

    asn_start = 30
    asn_end = asn_start + numberOfAs + 1
    asn_list = [asn for asn in range(asn_start, asn_end)]

    # Create Internet exchange
    ix8 = base.createInternetExchange(20)
    ix8.getPeeringLan().setDisplayName("New York-20")

    allAs = []
    
    for asn in asn_list:
        # Makers.makeStubAs(emu, base, asn, 20,[None,None])
        allAs.append(base.getAutonomousSystem(asn))
    
    ebgp.addRsPeers(20,asn_list)

    emu.addLayer(base)
    emu.addLayer(Routing())
    emu.addLayer(ebgp)
    emu.addLayer(Ibgp())
    emu.addLayer(Ospf())

    # emu.dump('base-component.bin')
    if isRender:
        emu.render()

        # Generate the Docker files
        emu.compile(Docker(), './output')

    return emu



# createTestNet(isRender=True)

