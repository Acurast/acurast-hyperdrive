# Tezos to Ethereum bridge

The bridge will monitor the `IBCF` contracts for `lock` calls, wait for signatures and then transmit the state to the Ethereum `IBCF client` contract.

### **Configuration file: [.env](.env)**

## Development

### Run

```sh
npm run dev
```

## Production

### Build

```sh
npm run build
```

### Run

```sh
npm run start
```

## Setup an Ethereum node

```sh
geth --syncmode light --goerli --http --http.port 8546 --rpc.allow-unprotected-txs
```
