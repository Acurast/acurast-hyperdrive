import React from 'react';
import WalletProvider from './WalletProvider';
import AppContext, {
    TezosBridgeStorage,
    EVMBridgeInfo,
    TezosValidatorInfo,
    TezosStateAggregatorInfo,
    EVMValidatorInfo,
} from './AppContext';
import Tezos from 'src/services/tezos';
import Constants from 'src/constants';
import Logger from 'src/services/logger';
import { ContractAbstraction } from '@taquito/taquito';
import * as IbcfSdk from 'ibcf-sdk';
import EthereumEthers, { Contract } from 'src/services/ethereum';
import WalletService from 'src/services/wallet';

// Cached contracts
let bridge_contract: ContractAbstraction<any> | undefined;
const validator_contract = new IbcfSdk.Tezos.Contracts.Validator.Contract(Tezos, Constants.tezos_validator);
const state_contract = new IbcfSdk.Tezos.Contracts.StateAggregator.Contract(Tezos, Constants.tezos_state_aggregator);

async function fetchTezosBridgeStorage(): Promise<TezosBridgeStorage> {
    if (!bridge_contract) {
        bridge_contract = await Tezos.contract.at(Constants.tezos_bridge);
    }
    const bridge = new IbcfSdk.Tezos.Contracts.Bridge.Contract(Tezos, Constants.tezos_bridge);
    const storage = await bridge.getStorage();
    const asset_address = storage.asset_address;
    const asset_contract = await Tezos.contract.at(asset_address);
    const asset_balance: string = await asset_contract.views
        .balance_of([{ owner: await WalletService.Tezos.getPkh(), token_id: '0' }])
        .read()
        .then((res) => res[0])
        .then(({ balance }) => balance.toString());

    // Get all wrap events
    const unwraps = await bridge.getUnwraps();

    return {
        asset: {
            address: asset_address,
            balance: asset_balance,
        },
        unwraps,
    };
}

async function fetchTezosValidatorInfo() {
    const latestSnapshot = await validator_contract.latestSnapshot();
    // let ethereumBlockNumber = (await EthereumEthers.getBlockNumber()) - 1;
    // const storage_root = (await validator_contract.storage<any>()).block_state_root as BigMapAbstraction;

    // const values = await storage_root.getMultipleValues<MichelsonMap<string, string>>(
    //     [...new Array(5)].map(() => ethereumBlockNumber--),
    // );

    const block_submissions: [string, string][] = [];
    //for (const [key, value] of values.entries()) {
    //    const submissions: Record<string, string[]> = {};
    //    for (const [key, _value] of value?.entries() || []) {
    //        if (submissions[_value]) {
    //            submissions[_value].push(key);
    //        } else {
    //            submissions[_value] = [key];
    //        }
    //    }
    //    if (Object.keys(submissions).length) {
    //        block_submissions.push([
    //            key as string,
    //            Object.entries(submissions).reduce((p, c) => (!p || p[1].length < c[1].length ? c : p), ['', []])[0],
    //        ]);
    //    }
    //}
    return {
        latestSnapshot,
    };
}

async function fetchTezosStateAggregatorInfo(): Promise<TezosStateAggregatorInfo> {
    const storage = await state_contract.getStorage();

    // const values = await stateAggregator.snapshot_level.getMultipleValues<{ root: string }>(
    //     stateAggregator.merkle_history_indexes,
    // );

    // const blocks: [BigNumber, string][] = [];
    // for (const [key, value] of values.entries()) {
    //     if (value) {
    //         blocks.push([key as BigNumber, value.root]);
    //     }
    // }

    return {
        snapshot_level: storage.snapshot_level,
        merkle_tree: storage.merkle_tree,
    };
}

async function fetchEvmBridgeInfo(): Promise<EVMBridgeInfo> {
    const bridge = new IbcfSdk.Ethereum.Contracts.Bridge.Contract(EthereumEthers.getSigner(), Constants.evm_bridge);
    const assetAddress = await bridge.getAssetAddress();
    const contract = new Contract(
        assetAddress,
        [
            {
                inputs: [
                    {
                        internalType: 'address',
                        name: 'account',
                        type: 'address',
                    },
                ],
                name: 'balanceOf',
                outputs: [
                    {
                        internalType: 'uint256',
                        name: '',
                        type: 'uint256',
                    },
                ],
                stateMutability: 'view',
                type: 'function',
            },
        ],
        EthereumEthers,
    );

    // Get all wrap events
    const wraps = await bridge.getWraps();

    return {
        asset: {
            address: assetAddress,
            balance: (await contract.balanceOf((await EthereumEthers.listAccounts())[0])).toString(),
        },
        wraps,
    };
}

async function fetchEvmValidatorInfo(): Promise<EVMValidatorInfo> {
    const validator = new IbcfSdk.Ethereum.Contracts.Validator.Contract(
        EthereumEthers.getSigner(),
        Constants.evm_validator,
    );

    const latestSnapshot = await validator.latestSnapshot();

    return {
        latestSnapshot,
    };
}

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isMounter = React.useRef(false);
    const [evmBridgeInfo, setEvmBridgeInfo] = React.useState<EVMBridgeInfo>();
    const [evmValidatorInfo, setEvmValidatorInfo] = React.useState<EVMValidatorInfo>();
    const [tezosBridgeStorage, setTezosBridgeStorage] = React.useState<TezosBridgeStorage>();
    const [tezosValidatorInfo, setTezosValidatorInfo] = React.useState<TezosValidatorInfo>();
    const [tezosStateAggregatorInfo, setTezosStateAggregatorInfo] = React.useState<TezosStateAggregatorInfo>();

    React.useEffect(() => {
        isMounter.current = true;

        const fetch = () => {
            // Ethereum
            fetchEvmBridgeInfo()
                .then((info) => {
                    if (isMounter.current) {
                        setEvmBridgeInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchEvmValidatorInfo()
                .then((info) => {
                    if (isMounter.current) {
                        setEvmValidatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            // Tezos
            fetchTezosStateAggregatorInfo()
                .then((info) => {
                    if (isMounter.current) {
                        setTezosStateAggregatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchTezosValidatorInfo()
                .then((info) => {
                    if (isMounter.current) {
                        setTezosValidatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchTezosBridgeStorage()
                .then((storage) => {
                    if (isMounter.current) {
                        setTezosBridgeStorage(storage);
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
                    bridgeStorage: tezosBridgeStorage,
                    validatorInfo: tezosValidatorInfo,
                    stateAggregatorInfo: tezosStateAggregatorInfo,
                },
                ethereum: {
                    bridgeInfo: evmBridgeInfo,
                    validatorInfo: evmValidatorInfo,
                },
            }}
        >
            <WalletProvider>{children}</WalletProvider>
        </AppContext.Provider>
    );
};

export default AppProvider;
