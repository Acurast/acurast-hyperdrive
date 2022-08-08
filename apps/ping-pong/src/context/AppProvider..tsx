import React from 'react';
import WalletProvider from './WalletProvider';
import AppContext, { TezosClientStorage, EthereumClientStorage, TezosStateAggregatorStorage } from './AppContext';
import Tezos from 'src/services/tezos';
import Constants from 'src/constants';
import Logger from 'src/services/logger';
import { BigMapAbstraction, ContractAbstraction, MichelsonMap } from '@taquito/taquito';
import Ethereum from 'src/services/ethereum';
import Web3 from 'web3';
import BigNumber from 'bignumber.js';

// Cached contracts
let client_contract: ContractAbstraction<any> | undefined;
let validator_contract: ContractAbstraction<any> | undefined;
let state_contract: ContractAbstraction<any> | undefined;

async function fetchTezosClientStorage(): Promise<TezosClientStorage> {
    if (!client_contract) {
        client_contract = await Tezos.contract.at(Constants.tezos_client);
    }
    return client_contract.storage<TezosClientStorage>();
}

async function fetchTezosValidatorStorage() {
    if (!validator_contract) {
        validator_contract = await Tezos.contract.at(Constants.tezos_validator);
    }
    let ethereumBlockNumber = (await Ethereum.eth.getBlockNumber()) - 1;
    const storage_root = (await validator_contract.storage<any>()).block_state_root as BigMapAbstraction;

    const values = await storage_root.getMultipleValues<MichelsonMap<string, string>>(
        [...new Array(5)].map(() => ethereumBlockNumber--),
    );

    const block_submissions: [string, string][] = [];
    for (const [key, value] of values.entries()) {
        const submissions: Record<string, string[]> = {};
        for (const [key, _value] of value?.entries() || []) {
            if (submissions[_value]) {
                submissions[_value].push(key);
            } else {
                submissions[_value] = [key];
            }
        }
        if (Object.keys(submissions).length) {
            block_submissions.push([
                key as string,
                Object.entries(submissions).reduce((p, c) => (!p || p[1].length < c[1].length ? c : p), ['', []])[0],
            ]);
        }
    }
    return block_submissions;
}

async function fetchTezosStateAggregatorStorage() {
    if (!state_contract) {
        state_contract = await Tezos.contract.at(Constants.tezos_state);
    }
    const stateAggregator = await state_contract.storage<TezosStateAggregatorStorage>();
    const values = await stateAggregator.merkle_history.getMultipleValues<{ root: string }>(
        stateAggregator.merkle_history_indexes,
    );

    const blocks: [BigNumber, string][] = [];
    for (const [key, value] of values.entries()) {
        if (value) {
            blocks.push([key as BigNumber, value.root]);
        }
    }

    return {
        ...stateAggregator,
        blocks,
    };
}

async function fetchEthClientStorage(): Promise<EthereumClientStorage> {
    const counter = Web3.utils
        .toAscii(await Ethereum.eth.getStorageAt(Constants.ethereum_client, 0))
        .replace(/[^0-9]*/g, '');
    return {
        counter,
    };
}

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isMounter = React.useRef(false);
    const [ethereumClientStorage, setEthereumClientStorage] = React.useState<EthereumClientStorage>();
    const [tezosClientStorage, setTezosClientStorage] = React.useState<TezosClientStorage>();
    const [tezosValidatorStorage, setTezosValidatorStorage] = React.useState<[string, string][]>();
    const [tezosStateStorage, setTezosStateStorage] = React.useState<TezosStateAggregatorStorage>();

    React.useEffect(() => {
        isMounter.current = true;

        const fetch = () => {
            // Ethereum
            fetchEthClientStorage()
                .then((storage) => {
                    if (isMounter.current) {
                        setEthereumClientStorage(storage);
                    }
                })
                .catch(Logger.debug);
            // Tezos
            fetchTezosStateAggregatorStorage()
                .then((storage) => {
                    if (isMounter.current) {
                        setTezosStateStorage(storage);
                    }
                })
                .catch(Logger.debug);
            fetchTezosValidatorStorage()
                .then((storage) => {
                    if (isMounter.current) {
                        setTezosValidatorStorage(storage);
                    }
                })
                .catch(Logger.debug);
            fetchTezosClientStorage()
                .then((storage) => {
                    if (isMounter.current) {
                        setTezosClientStorage(storage);
                    }
                })
                .catch(Logger.debug);
        };
        fetch(); // First fetch

        const cron = setInterval(fetch, 5000 /* 5 seconds */);
        return () => {
            isMounter.current = false;
            clearInterval(cron);
        };
    }, []);

    return (
        <AppContext.Provider
            value={{
                tezos: {
                    clientStorage: tezosClientStorage,
                    validatorStorage: tezosValidatorStorage,
                    stateAggregatorStorage: tezosStateStorage,
                },
                ethereum: {
                    clientStorage: ethereumClientStorage,
                },
            }}
        >
            <WalletProvider>{children}</WalletProvider>
        </AppContext.Provider>
    );
};

export default AppProvider;
