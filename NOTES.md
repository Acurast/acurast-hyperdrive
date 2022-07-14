## Gas costs

Values from [michelson_v1_gas.ml](https://gitlab.com/tezos/tezos/-/blob/master/src/proto_014_PtKathma/lib_protocol/michelson_v1_gas.ml)

```ml
(* Base cost per instruction *)

BLAKE2B: 430
SHA256: 600
SHA512: 680
SHA3: 1350
KECCAK: 1350
```

Ethereum does not support `BLAKE2B` natively. More info at [EIP: BLAKE2b F Compression Function Precompile](https://github.com/ethereum/EIPs/issues/152)
