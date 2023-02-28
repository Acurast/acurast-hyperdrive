import React from 'react';
import WalletProvider from './WalletProvider';
import AppContext, {
    TezosBridgeInfo,
    EVMBridgeInfo,
    TezosValidatorInfo,
    TezosStateAggregatorInfo,
    EVMValidatorInfo,
    EVMCrowdfundInfo,
    TezosCrowdfundInfo,
    Network,
} from './AppContext';
import Tezos from 'src/services/tezos';
import Constants from 'src/constants';
import Logger from 'src/services/logger';
import { MichelsonMap } from '@taquito/taquito';
import * as IbcfSdk from 'ibcf-sdk';
import EthereumEthers, { Contract } from 'src/services/ethereum';
import WalletService from 'src/services/wallet';
import BigNumber from 'bignumber.js';

// Cached contracts
const validator_contract = (address: string) => new IbcfSdk.Tezos.Contracts.Validator.Contract(Tezos, address);
const state_contract = (address: string) => new IbcfSdk.Tezos.Contracts.StateAggregator.Contract(Tezos, address);

async function fetchTezosBridgeInfo(network: Network): Promise<TezosBridgeInfo> {
    const bridge = new IbcfSdk.Tezos.Contracts.Bridge.Contract(Tezos, Constants[network].tezos_bridge);
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

async function fetchTezosCrowdfundInfo(network: Network): Promise<TezosCrowdfundInfo> {
    const crowdfunding_contract = await Tezos.contract.at(Constants[network].tezos_crowdfunding);
    const storage = await crowdfunding_contract.storage<any>();

    const tezos_funding: MichelsonMap<string, BigNumber> = storage.tezos_funding;
    const eth_funding: MichelsonMap<string, BigNumber> = storage.eth_funding;

    const tezos = [];
    for (const [funder, amount] of tezos_funding.entries()) {
        tezos.push({
            funder,
            amount: amount.toNumber(),
        });
    }

    const eth = [];
    for (const [funder, amount] of eth_funding.entries()) {
        eth.push({
            funder,
            amount: amount.toNumber(),
        });
    }

    return {
        tezos_funding: tezos,
        eth_funding: eth,
    };
}

async function fetchTezosValidatorInfo(network: Network) {
    const latestSnapshot = await validator_contract(Constants[network].tezos_validator).latestSnapshot();
    return {
        latestSnapshot,
    };
}

async function fetchTezosStateAggregatorInfo(network: Network): Promise<TezosStateAggregatorInfo> {
    const storage = await state_contract(Constants[network].tezos_state_aggregator).getStorage();

    return {
        snapshot_level: storage.snapshot_level,
        merkle_tree: storage.merkle_tree,
    };
}

async function fetchEvmBridgeInfo(network: Network): Promise<EVMBridgeInfo> {
    const bridge = new IbcfSdk.Ethereum.Contracts.Bridge.Contract(
        EthereumEthers.getSigner(),
        Constants[network].evm_bridge,
    );
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
    const block = await EthereumEthers.getBlockNumber();
    const wraps = await bridge.getWraps(block - 1000, block);

    return {
        asset: {
            address: assetAddress,
            balance: (await contract.balanceOf((await EthereumEthers.listAccounts())[0])).toString(),
        },
        wraps,
    };
}

async function fetchEvmCrowdfundInfo(network: Network): Promise<EVMCrowdfundInfo> {
    const contract = new Contract(
        Constants[network].evm_crowdfunding,
        [
            {
                anonymous: false,
                inputs: [
                    {
                        indexed: false,
                        internalType: 'address',
                        name: 'funder',
                        type: 'address',
                    },
                    {
                        indexed: false,
                        internalType: 'uint256',
                        name: 'amount',
                        type: 'uint256',
                    },
                    {
                        indexed: false,
                        internalType: 'uint256',
                        name: 'nonce',
                        type: 'uint256',
                    },
                ],
                name: 'Funding',
                type: 'event',
            },
        ],
        EthereumEthers,
    );

    const block = await EthereumEthers.getBlockNumber();
    const funding = await contract
        .queryFilter(contract.filters.Funding(), block - 1000, block)
        .then((events) =>
            events.map((event) => ({
                funder: event.args?.[0],
                amount: BigNumber(event.args?.[1].toString()),
                nonce: BigNumber(event.args?.[2].toString()),
            })),
        )
        .catch((err) => {
            console.log('Err:', err);
            return [];
        });

    return {
        funding,
    };
}

async function fetchEvmValidatorInfo(network: Network): Promise<EVMValidatorInfo> {
    const validator = new IbcfSdk.Ethereum.Contracts.Validator.Contract(
        EthereumEthers.getSigner(),
        Constants[network].evm_validator,
    );

    const latestSnapshot = await validator.latestSnapshot();

    return {
        latestSnapshot,
    };
}

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isMounter = React.useRef(false);
    const [network, setNetwork] = React.useState(Network.Ethereum);
    const [evmBridgeInfo, setEvmBridgeInfo] = React.useState<EVMBridgeInfo>();
    const [evmCrowdfundInfo, setEvmCrowdfundInfo] = React.useState<EVMCrowdfundInfo>();
    const [evmValidatorInfo, setEvmValidatorInfo] = React.useState<EVMValidatorInfo>();
    const [tezosBridgeInfo, setTezosBridgeInfo] = React.useState<TezosBridgeInfo>();
    const [tezosCrowdfundInfo, setTezosCrowdfundInfo] = React.useState<TezosCrowdfundInfo>();
    const [tezosValidatorInfo, setTezosValidatorInfo] = React.useState<TezosValidatorInfo>();
    const [tezosStateAggregatorInfo, setTezosStateAggregatorInfo] = React.useState<TezosStateAggregatorInfo>();

    React.useEffect(() => {
        isMounter.current = true;

        const fetch = () => {
            // Ethereum
            fetchEvmBridgeInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setEvmBridgeInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchEvmCrowdfundInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setEvmCrowdfundInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchEvmValidatorInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setEvmValidatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            // Tezos
            fetchTezosStateAggregatorInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setTezosStateAggregatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchTezosValidatorInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setTezosValidatorInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchTezosBridgeInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setTezosBridgeInfo(info);
                    }
                })
                .catch(Logger.debug);
            fetchTezosCrowdfundInfo(network)
                .then((info) => {
                    if (isMounter.current) {
                        setTezosCrowdfundInfo(info);
                    }
                })
                .catch(Logger.debug);
        };
        fetch(); // First fetch

        const cron = setInterval(fetch, 10000 /* 5 seconds */);
        return () => {
            isMounter.current = false;
            clearInterval(cron);
        };
    }, [network]);

    return (
        <AppContext.Provider
            value={{
                network,
                updateNetwork: async (network: Network) => {
                    if (network != Network.Ethereum) {
                        try {
                            await (window as any).ethereum.request({
                                method: 'wallet_addEthereumChain',
                                params: [
                                    {
                                        chainId: Constants[network].ethChainId,
                                        chainName: network,
                                        rpcUrls: Constants[network].rpcUrls,
                                    },
                                ],
                            });
                        } catch (e) {
                            Logger.trace(e);
                        }
                    }
                    EthereumEthers.network.chainId = Number(Constants[network].ethChainId);
                    await (window as any).ethereum
                        .request({
                            method: 'wallet_switchEthereumChain',
                            params: [{ chainId: Constants[network].ethChainId }],
                        })
                        .then(() => setNetwork(network));
                },
                tezos: {
                    bridgeInfo: tezosBridgeInfo,
                    validatorInfo: tezosValidatorInfo,
                    stateAggregatorInfo: tezosStateAggregatorInfo,
                    crowdfundInfo: tezosCrowdfundInfo,
                },
                ethereum: {
                    bridgeInfo: evmBridgeInfo,
                    validatorInfo: evmValidatorInfo,
                    crowdfundInfo: evmCrowdfundInfo,
                },
            }}
        >
            <WalletProvider>{children}</WalletProvider>
        </AppContext.Provider>
    );
};

export default AppProvider;
