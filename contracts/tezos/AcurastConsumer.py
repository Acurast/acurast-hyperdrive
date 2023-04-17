# ----------------------------------------------------------------------------
# This contract is an example of an acurast consumer on Tezos blockchain.
#
# It allows contracts to receive job fulfillments from Acurast processors.
# ----------------------------------------------------------------------------

import smartpy as sp

class Entrypoint:
    SetJobId = "set_job_id"
    AssignProcessor = "assign_processor"
    Fulfill = "fulfill"

class Type:
    SetJobId = sp.TNat
    AssignProcessor = sp.TRecord(job_id=sp.TNat, processor=sp.TAddress).right_comb()
    Fulfill = sp.TRecord(job_id=sp.TNat, payload=sp.TBytes).right_comb()

class Inlined:
    @staticmethod
    def failIfNotAcurastProxy(self):
        """
        This method when used, ensures that only the acurast contract is allowed to call a given entrypoint
        """
        sp.verify(
            self.data.config.acurast_proxy == sp.sender, "NOT_ACURAST_PROXY"
        )

    @staticmethod
    def failIfNotAcurastProcessor(self):
        """
        This method when used, ensures that only assigned processors are allowed to call a given entrypoint
        """
        sp.verify(
            self.data.config.acurast_processors.contains(sp.sender), "PROCESSOR_NOT_ALLOWED"
        )

    @staticmethod
    def failIfJobIsUnknown(self, job_id):
        """
        This method when used, ensures that only known jobs are processed
        """
        sp.verify(self.data.config.job_id == sp.some(job_id), "JOB_UNKOWN")

class AcurastConsumer(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config = sp.TRecord(
                    job_id = sp.TOption(sp.TNat),
                    acurast_proxy = sp.TAddress,
                    acurast_processors = sp.TSet(sp.TAddress)
                )
                # Add custom storage here ...
            )
        )

    @sp.entry_point(name=Entrypoint.SetJobId, parameter_type=Type.SetJobId)
    def set_job_id(self, job_id):
        Inlined.failIfNotAcurastProxy(self)
        sp.verify(self.data.config.job_id == sp.none, "JOB_ID_ALREADY_SET")
        self.data.config.job_id = sp.some(job_id)

    @sp.entry_point(name=Entrypoint.AssignProcessor, parameter_type=Type.AssignProcessor)
    def assign_processor(self, arg):
        Inlined.failIfNotAcurastProxy(self)
        Inlined.failIfJobIsUnknown(self, arg.job_id)
        # Whitelist processor
        self.data.config.acurast_processors.add(arg.processor)

    @sp.entry_point(name=Entrypoint.Fulfill, parameter_type=Type.Fulfill)
    def fulfill(self, arg):
        Inlined.failIfNotAcurastProcessor(self)
        Inlined.failIfJobIsUnknown(self, arg.job_id)

        # Process fulfill payload ...
        payload = arg.payload
