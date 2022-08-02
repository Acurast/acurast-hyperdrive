import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface


class Error:
    EXPECTING_PONG = "EXPECTING_PONG"
    EXPECTING_PING = "EXPECTING_PING"


@staticmethod
def string_of_nat(number):
    """Convert an int into a string"""
    c = sp.map({x: str(x) for x in range(0, 10)})
    negative = number < 0
    x = sp.local("x", number)
    arr = sp.local("arr", [])

    with sp.if_(x.value == 0):
        arr.value.push("0")
    with sp.while_(0 < x.value):
        arr.value.push(c[x.value % 10])
        x.value //= 10

    result = sp.local("result", sp.concat(arr.value))
    with sp.if_(negative):
        result.value = "-" + result.value

    return result.value


class IBCF_Client(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                eth_contract=sp.TBytes,
                storage_slot=sp.TBytes,
                ibcf_tezos_state=sp.TAddress,
                ibcf_eth_validator=sp.TAddress,
                counter=sp.TNat,
                latest_sent_payload=sp.TBytes,
                latest_received_payload=sp.TBytes,
            )
        )

    @sp.entry_point()
    def update_storage(self, param):
        self.data = param

    @sp.entry_point()
    def ping(self):
        # Pings can only heappen when counter is even
        sp.verify(self.data.counter % 2 == 0, Error.EXPECTING_PONG)

        # Increase counter
        self.data.counter += 1
        packed_counter = sp.compute(sp.pack(string_of_nat(self.data.counter)))
        self.data.latest_sent_payload = packed_counter

        # Send ping
        param = sp.record(key=sp.pack("counter"), value=packed_counter)
        contract = sp.contract(
            Type.InsertArgument, self.data.ibcf_tezos_state, "insert"
        ).open_some("INVALID_CONTRACT")
        sp.transfer(param, sp.mutez(0), contract)

    @sp.entry_point()
    def pong(self, param):
        sp.set_type(param, sp.TRecord(block_number=sp.TNat, storage_proof=sp.TBytes))

        # Pongs can only happen when counter is odd
        sp.verify(self.data.counter % 2 == 1, Error.EXPECTING_PING)

        # Increase counter
        self.data.counter += 1

        self.data.latest_received_payload = sp.view(
            "get_storage",
            self.data.ibcf_eth_validator,
            sp.set_type_expr(
                sp.record(
                    account=self.data.eth_contract,
                    storage_slot=self.data.storage_slot,
                    block_number=param.block_number,
                    storage_proof=param.storage_proof,
                ),
                ValidatiorInterface.Get_storage_argument,
            ),
            t=sp.TBytes,
        ).open_some("INVALID_VIEW")
