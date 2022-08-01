import smartpy as sp

from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator

sp.add_compilation_target("IBCF_Eth_Validator", IBCF_Eth_Validator())
