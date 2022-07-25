import smartpy as sp

from contracts.tezos.IBCF_Client import IBCF_Client

sp.add_compilation_target("IBCF_Client", IBCF_Client())
