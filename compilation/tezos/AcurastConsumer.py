import smartpy as sp

from contracts.tezos.AcurastConsumer import AcurastConsumer

sp.add_compilation_target(
    "AcurastConsumer",
    AcurastConsumer(),
    storage=sp.record(
        config=sp.record(
            acurast_proxy = sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")
        )
    ),
)
