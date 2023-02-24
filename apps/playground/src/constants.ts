import { Network } from './context/AppContext';

const Constants = {
    network: 'custom',
    rpc: 'https://tezos-ghostnet-node-1.diamond.papers.tech',
    [Network.Ethereum]: {
        network: 'custom',
        ethChainId: '0x5',
        rpc: 'https://tezos-ghostnet-node-1.diamond.papers.tech',
        tezos_bridge: 'KT1AyXoM57cyXv8yZLn4nBNzVSmCJKMtuEdf',
        tezos_crowdfunding: 'KT1RUuZ1D8UZdY59cLjbC2GCCqP4HUvDeiix',
        tezos_validator: 'KT1QfWxeYitE4NXvC4caBJpwimzxZygqPJ9F',
        tezos_state_aggregator: 'KT1B8F7BhA2EeGQvPFpaVStd99ZDSzwrAcBL',
        evm_bridge: '0x945BEeA0C9C8052764e8Ef54a571386Cd1027BF1',
        evm_crowdfunding: '0x79a20860c063a70EB483f5b6fb70b9CaDb022729',
        evm_validator: '0xE258F751a56343b722263cbF9Fdf3e71F1815cAA',
        etherscan: 'https://goerli.etherscan.io',
        tzkt: 'https://ghostnet.tzkt.io',
    },
    [Network.Polygon]: {
        network: 'custom',
        ethChainId: '0x13881',
        rpc: 'https://tezos-ghostnet-node-1.diamond.papers.tech',
        tezos_bridge: 'KT1HEDc9u625CvuBnVcW4rGwj3y7un5X4FQn',
        tezos_crowdfunding: 'KT1BeAbWcQtdaLzFS4XRgCThHbY6Ub4xso1M',
        tezos_validator: 'KT1Gf13zVZuQAQF1zfMVYWxTye3ghqK9HQLY',
        tezos_state_aggregator: 'KT1B8F7BhA2EeGQvPFpaVStd99ZDSzwrAcBL',
        evm_bridge: '0xB709A925CED4b900bFF971C2c88AFDD1767aEF9F',
        evm_crowdfunding: '0xD392928Bac5995c2bE96fE75583B2C3F250d9aAd',
        evm_validator: '0x6a8fE13d57998834feA5181607a8a3f4Cd0B42d4',
        etherscan: 'https://mumbai.polygonscan.com/',
        tzkt: 'https://ghostnet.tzkt.io',
    },
};

export default Constants;
