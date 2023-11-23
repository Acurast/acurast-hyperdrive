import React from 'react';
import WalletProvider from './WalletProvider';
import AppContext, { AeternityBridgeInfo, BridgeMovement, EVMBridgeInfo, Network } from './AppContext';
import Aeternity from 'src/services/aeternity';
import Constants from 'src/constants';
import Logger from 'src/services/logger';
import EthereumEthers, { Contract } from 'src/services/ethereum';
import BigNumber from 'bignumber.js';

async function fetchAeternityBridgeInfo(): Promise<AeternityBridgeInfo> {
    const bridge_contract = await Aeternity.initializeContract({
        aci: Constants.aeternity.bridge_aci,
        address: Constants.aeternity.bridge_address,
    });
    const { decodedResult: asset_address } = await bridge_contract.asset();

    const asset_contract = await Aeternity.initializeContract({
        aci: Constants.aeternity.asset_aci,
        address: asset_address,
    });
    const { decodedResult: asset_balance } = await asset_contract.balance(Aeternity.address);

    const { decodedResult: movements_out } = await bridge_contract.movements_out();
    console.log(Aeternity.address, asset_balance, movements_out);

    const movements = [];
    for (const [key, value] of movements_out) {
        movements.push({
            nonce: key,
            ...value,
        });
    }
    console.log(movements);

    return {
        asset: {
            address: asset_address,
            balance: asset_balance.toString(),
        },
        movements,
    };
}

async function fetchEvmBridgeInfo(network: Network): Promise<EVMBridgeInfo> {
    const account = (await EthereumEthers.listAccounts())[0];
    const bridge = new Contract(Constants[network].bridge_address, Constants[network].bridge_abi, EthereumEthers);

    const assetAddress = await bridge.asset();

    const asset = new Contract(
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

    console.log(assetAddress);

    // Get all movements
    //const block = await EthereumEthers.getBlockNumber();
    const movements: BridgeMovement[] = await bridge
        .queryFilter(bridge.filters.BridgeOut())
        .then((events) =>
            events.map((event) => ({
                sender: '',
                destination: event.args?.[0],
                amount: BigInt(event.args?.[1].toString()),
                nonce: BigInt(event.args?.[2].toString()),
            })),
        )
        .catch((err) => {
            console.log('Err:', err);
            return [];
        });

    return {
        account,
        asset: {
            address: assetAddress,
            balance: (await asset.balanceOf(account)).toString(),
        },
        movements,
    };
}

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isMounter = React.useRef(false);
    const [network, setNetwork] = React.useState(Network.Ethereum);
    const [evmBridgeInfo, setEvmBridgeInfo] = React.useState<EVMBridgeInfo>();
    const [aeternityBridgeInfo, setAeternityBridgeInfo] = React.useState<AeternityBridgeInfo>();

    React.useEffect(() => {
        isMounter.current = true;

        const fetch = () => {
            // Ethereum
            fetchEvmBridgeInfo(network).then((info) => {
                if (isMounter.current) {
                    setEvmBridgeInfo(info);
                }
            });
            // Aeternity
            fetchAeternityBridgeInfo()
                .then((info) => {
                    if (isMounter.current) {
                        setAeternityBridgeInfo(info);
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
                    EthereumEthers.network.chainId = Number(Constants[network].ethChainId);
                    await (window as any).ethereum
                        .request({
                            method: 'wallet_switchEthereumChain',
                            params: [{ chainId: Constants[network].ethChainId }],
                        })
                        .then(() => setNetwork(network));
                },
                aeternity: {
                    bridgeInfo: aeternityBridgeInfo,
                },
                ethereum: {
                    bridgeInfo: evmBridgeInfo,
                },
            }}
        >
            <WalletProvider>{children}</WalletProvider>
        </AppContext.Provider>
    );
};

export default AppProvider;
