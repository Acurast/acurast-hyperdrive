# ----------------------------------------------------------------------------
# This contract is an example of an acurast consumer on Tezos blockchain.
#
# It allows contracts to receive job fulfillments from Acurast processors.
# ----------------------------------------------------------------------------

import smartpy as sp


class Entrypoint:
    Fulfill = "fulfill"


class Type:
    Fulfill = sp.TRecord(job_id=sp.TNat, payload=sp.TBytes).right_comb()


class Inlined:
    @staticmethod
    def failIfNotAcurastProxy(self):
        """
        This method when used, ensures that only the acurast contract is allowed to call a given entrypoint
        """
        sp.verify(self.data.config.acurast_proxy == sp.sender, "NOT_ACURAST_PROXY")


class AcurastConsumer(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    acurast_proxy=sp.TAddress,
                )
                # Add custom storage here ...
            )
        )

    @sp.entry_point(name=Entrypoint.Fulfill, parameter_type=Type.Fulfill)
    def fulfill(self, arg):
        Inlined.failIfNotAcurastProxy(self)

        # Process fulfill payload ...
        payload = arg.payload
