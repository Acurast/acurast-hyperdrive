import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type


class IBCF_Client(sp.Contract):
    def __init__(self):
        self.init_type(sp.TRecord(ibcf_address=sp.TAddress, locked=sp.TNat))

    @sp.entry_point()
    def lock(self, param):
        sp.set_type(param, sp.TRecord(token_id=sp.TNat, amount=sp.TNat))

        self.data.locked = param.amount
        param = sp.record(key=sp.pack(param.token_id), value=sp.pack(param.amount))

        contract = sp.contract(
            Type.InsertArgument, self.data.ibcf_address, "insert"
        ).open_some("INVALID_CONTRACT")
        sp.transfer(param, sp.mutez(0), contract)

    @sp.entry_point()
    def unlock(self, param):
        sp.set_type(param, sp.TRecord(token_id=sp.TNat, amount=sp.TNat))
        self.data.locked = param.amount
