import smartpy as sp

from contracts.tezos.MMR_Validator import MMR_Validator

sp.add_compilation_target("MMR_Validator", MMR_Validator())
