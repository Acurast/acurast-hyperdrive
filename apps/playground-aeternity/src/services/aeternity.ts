import {
    AeSdkAepp,
    BrowserWindowMessageConnection,
    Node,
    SUBSCRIPTION_TYPES,
    walletDetector,
} from '@aeternity/aepp-sdk';

import Constants from 'src/constants';

const Aeternity = new AeSdkAepp({
    name: 'Bridge demo',
    nodes: [{ name: 'testnet', instance: new Node(Constants.aeternity.rpc) }],
    onNetworkChange: async ({ networkId }) => {
        const [{ name }] = (await Aeternity.getNodesInPool()).filter((node) => node.nodeNetworkId === networkId);
        Aeternity.selectNode(name);
        console.log('setNetworkId', networkId);
    },
    onAddressChange: ({ current }) => console.log(Object.keys(current)[0]),
    onDisconnect: () => console.log('Aepp is disconnected'),
});

export const connect = async () => {
    return new Promise((resolve, reject) => {
        const handleWallets = async ({ wallets, newWallet }: any) => {
            const wallet: any = wallets['Superhero Wallet'];
            if (wallet) {
                const walletInfo = await Aeternity.connectToWallet(wallet.getConnection());
                const {
                    address: { current },
                } = await Aeternity.subscribeAddress(SUBSCRIPTION_TYPES.subscribe, 'connected');
                console.log(walletInfo, current);
                resolve(current);
            }
            stopScan();
            reject();
        };

        const scannerConnection = new BrowserWindowMessageConnection();
        const stopScan = walletDetector(scannerConnection, handleWallets);
    });
};

export default Aeternity;
