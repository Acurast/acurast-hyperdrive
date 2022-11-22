# IBCF state trasmitter

The transmitter will submit the root state of every block to the respective contracts. The root state submitted in this step is then used to validate the merkle proofs.

### **Configuration file: [.env](.env)**

### Build

```sh
npm run build
```

### Run

```sh
npm run start tezos_monitor

or

npm run start eth_monitor
```

## Setup an Ethereum node

```sh
geth --syncmode light --goerli --http --http.port 8546 --rpc.allow-unprotected-txs
```
