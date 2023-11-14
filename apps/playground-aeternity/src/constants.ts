import { Network } from './context/AppContext';

const Constants = {
    network: 'custom',
    rpc: 'https://tezos-ghostnet-node-1.diamond.papers.tech',
    [Network.Ethereum]: {
        bridge_address: '0x43733e95b0e5e6b57f863c19adadc04866da87bd',
        bridge_abi: [
            {
                inputs: [
                    {
                        internalType: 'contract MintableERC20',
                        name: '_asset',
                        type: 'address',
                    },
                ],
                stateMutability: 'nonpayable',
                type: 'constructor',
            },
            {
                anonymous: false,
                inputs: [
                    {
                        indexed: false,
                        internalType: 'address',
                        name: 'destination',
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
                        name: 'in_nonce',
                        type: 'uint256',
                    },
                ],
                name: 'BridgeIn',
                type: 'event',
            },
            {
                anonymous: false,
                inputs: [
                    {
                        indexed: false,
                        internalType: 'string',
                        name: 'destination',
                        type: 'string',
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
                        name: 'out_nonce',
                        type: 'uint256',
                    },
                ],
                name: 'BridgeOut',
                type: 'event',
            },
            {
                inputs: [],
                name: 'asset',
                outputs: [
                    {
                        internalType: 'contract MintableERC20',
                        name: '',
                        type: 'address',
                    },
                ],
                stateMutability: 'view',
                type: 'function',
            },
            {
                inputs: [
                    {
                        internalType: 'uint256',
                        name: '',
                        type: 'uint256',
                    },
                ],
                name: 'bridge_actions',
                outputs: [
                    {
                        internalType: 'address',
                        name: 'sender',
                        type: 'address',
                    },
                    {
                        internalType: 'string',
                        name: 'destination',
                        type: 'string',
                    },
                    {
                        internalType: 'uint256',
                        name: 'amount',
                        type: 'uint256',
                    },
                ],
                stateMutability: 'view',
                type: 'function',
            },
            {
                inputs: [
                    {
                        internalType: 'address',
                        name: 'destination',
                        type: 'address',
                    },
                    {
                        internalType: 'uint256',
                        name: 'amount',
                        type: 'uint256',
                    },
                ],
                name: 'bridge_in',
                outputs: [],
                stateMutability: 'nonpayable',
                type: 'function',
            },
            {
                inputs: [
                    {
                        internalType: 'string',
                        name: 'destination',
                        type: 'string',
                    },
                    {
                        internalType: 'uint256',
                        name: 'amount',
                        type: 'uint256',
                    },
                ],
                name: 'bridge_out',
                outputs: [],
                stateMutability: 'nonpayable',
                type: 'function',
            },
            {
                inputs: [],
                name: 'in_counter',
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
            {
                inputs: [],
                name: 'out_counter',
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
            {
                inputs: [],
                name: 'owner',
                outputs: [
                    {
                        internalType: 'address',
                        name: '',
                        type: 'address',
                    },
                ],
                stateMutability: 'view',
                type: 'function',
            },
            {
                inputs: [],
                name: 'processor',
                outputs: [
                    {
                        internalType: 'address',
                        name: '',
                        type: 'address',
                    },
                ],
                stateMutability: 'view',
                type: 'function',
            },
            {
                inputs: [
                    {
                        internalType: 'address',
                        name: '_processor',
                        type: 'address',
                    },
                ],
                name: 'set_processor',
                outputs: [],
                stateMutability: 'nonpayable',
                type: 'function',
            },
        ],
        rpcUrls: ['https://rpc.ankr.com/eth_goerli'],
        ethChainId: '0xaa36a7',
        etherscan: 'https://sepolia.etherscan.io',
    },
    aeternity: {
        explorer: 'https://testnet.aescan.io',
        rpc: 'https://testnet.aeternity.io',
        bridge_address: 'ct_2staJWJ8F77Kpo6mVETWkghyAtbaKJjUNZQj7evJbWZ7PruU42' as `ct_${string}`,
        bridge_aci: [
            { namespace: { name: 'Option', typedefs: [] } },
            { namespace: { name: 'ListInternal', typedefs: [] } },
            { namespace: { name: 'List', typedefs: [] } },
            { namespace: { name: 'String', typedefs: [] } },
            {
                contract: {
                    event: {
                        variant: [
                            { Transfer: ['address', 'address', 'int'] },
                            { Allowance: ['address', 'address', 'int'] },
                            { Burn: ['address', 'int'] },
                            { Mint: ['address', 'int'] },
                            { Swap: ['address', 'int'] },
                        ],
                    },
                    functions: [
                        {
                            arguments: [],
                            name: 'aex9_extensions',
                            payable: false,
                            returns: { list: ['string'] },
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'meta_info',
                            payable: false,
                            returns: 'FungibleTokenFullInterface.meta_info',
                            stateful: false,
                        },
                        { arguments: [], name: 'total_supply', payable: false, returns: 'int', stateful: false },
                        { arguments: [], name: 'owner', payable: false, returns: 'address', stateful: false },
                        {
                            arguments: [],
                            name: 'balances',
                            payable: false,
                            returns: { map: ['address', 'int'] },
                            stateful: false,
                        },
                        {
                            arguments: [{ name: '_1', type: 'address' }],
                            name: 'balance',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [
                                { name: '_1', type: 'address' },
                                { name: '_2', type: 'int' },
                            ],
                            name: 'transfer',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [],
                            name: 'allowances',
                            payable: false,
                            returns: 'FungibleTokenFullInterface.allowances',
                            stateful: false,
                        },
                        {
                            arguments: [{ name: '_1', type: 'FungibleTokenFullInterface.allowance_accounts' }],
                            name: 'allowance',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [{ name: '_1', type: 'address' }],
                            name: 'allowance_for_caller',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [
                                { name: '_1', type: 'address' },
                                { name: '_2', type: 'address' },
                                { name: '_3', type: 'int' },
                            ],
                            name: 'transfer_allowance',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: '_1', type: 'address' },
                                { name: '_2', type: 'int' },
                            ],
                            name: 'create_allowance',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: '_1', type: 'address' },
                                { name: '_2', type: 'int' },
                            ],
                            name: 'change_allowance',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [{ name: '_1', type: 'address' }],
                            name: 'reset_allowance',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [{ name: '_1', type: 'int' }],
                            name: 'burn',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: '_1', type: 'address' },
                                { name: '_2', type: 'int' },
                            ],
                            name: 'mint',
                            payable: false,
                            returns: 'unit',
                            stateful: true,
                        },
                        { arguments: [], name: 'swap', payable: false, returns: 'unit', stateful: true },
                        {
                            arguments: [{ name: '_1', type: 'address' }],
                            name: 'check_swap',
                            payable: false,
                            returns: 'int',
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'swapped',
                            payable: false,
                            returns: { map: ['address', 'int'] },
                            stateful: false,
                        },
                    ],
                    kind: 'contract_interface',
                    name: 'FungibleTokenFullInterface',
                    payable: false,
                    typedefs: [
                        {
                            name: 'meta_info',
                            typedef: {
                                record: [
                                    { name: 'name', type: 'string' },
                                    { name: 'symbol', type: 'string' },
                                    { name: 'decimals', type: 'int' },
                                ],
                            },
                            vars: [],
                        },
                        {
                            name: 'allowance_accounts',
                            typedef: {
                                record: [
                                    { name: 'from_account', type: 'address' },
                                    { name: 'for_account', type: 'address' },
                                ],
                            },
                            vars: [],
                        },
                        {
                            name: 'allowances',
                            typedef: { map: ['FungibleTokenFullInterface.allowance_accounts', 'int'] },
                            vars: [],
                        },
                    ],
                },
            },
            {
                contract: {
                    functions: [
                        {
                            arguments: [{ name: 'asset', type: 'FungibleTokenFullInterface' }],
                            name: 'init',
                            payable: false,
                            returns: 'Bridge.state',
                            stateful: true,
                        },
                        {
                            arguments: [{ name: 'processor', type: 'address' }],
                            name: 'set_processor',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [{ name: 'x#1', type: { tuple: ['string', 'int'] } }],
                            name: 'bridge_out',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [{ name: 'x#1', type: { tuple: ['int', 'address', 'int'] } }],
                            name: 'bridge_in',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [],
                            name: 'asset',
                            payable: false,
                            returns: 'FungibleTokenFullInterface',
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'movements_out',
                            payable: false,
                            returns: { map: ['int', 'Bridge.bridge_action'] },
                            stateful: false,
                        },
                    ],
                    kind: 'contract_main',
                    name: 'Bridge',
                    payable: false,
                    state: {
                        record: [
                            { name: 'asset', type: 'FungibleTokenFullInterface' },
                            { name: 'evm_bridge', type: { map: ['int', 'Bridge.bridge_action'] } },
                            { name: 'out_counter', type: 'int' },
                            { name: 'in_counter', type: 'int' },
                            { name: 'owner', type: 'address' },
                            { name: 'processor', type: 'address' },
                        ],
                    },
                    typedefs: [
                        {
                            name: 'bridge_action',
                            typedef: {
                                record: [
                                    { name: 'sender', type: 'address' },
                                    { name: 'destination', type: 'string' },
                                    { name: 'amount', type: 'int' },
                                ],
                            },
                            vars: [],
                        },
                    ],
                },
            },
        ],
        asset_aci: [
            { namespace: { name: 'Option', typedefs: [] } },
            { namespace: { name: 'ListInternal', typedefs: [] } },
            { namespace: { name: 'List', typedefs: [] } },
            { namespace: { name: 'String', typedefs: [] } },
            {
                contract: {
                    event: {
                        variant: [
                            { Transfer: ['address', 'address', 'int'] },
                            { Allowance: ['address', 'address', 'int'] },
                            { Burn: ['address', 'int'] },
                            { Mint: ['address', 'int'] },
                            { Swap: ['address', 'int'] },
                        ],
                    },
                    functions: [
                        {
                            arguments: [],
                            name: 'aex9_extensions',
                            payable: false,
                            returns: { list: ['string'] },
                            stateful: false,
                        },
                        {
                            arguments: [
                                { name: 'name', type: 'string' },
                                { name: 'decimals', type: 'int' },
                                { name: 'symbol', type: 'string' },
                                { name: 'initial_owner_balance', type: { option: ['int'] } },
                            ],
                            name: 'init',
                            payable: false,
                            returns: 'FungibleTokenFull.state',
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'meta_info',
                            payable: false,
                            returns: 'FungibleTokenFull.meta_info',
                            stateful: false,
                        },
                        { arguments: [], name: 'total_supply', payable: false, returns: 'int', stateful: false },
                        { arguments: [], name: 'owner', payable: false, returns: 'address', stateful: false },
                        {
                            arguments: [],
                            name: 'balances',
                            payable: false,
                            returns: 'FungibleTokenFull.balances',
                            stateful: false,
                        },
                        {
                            arguments: [{ name: 'account', type: 'address' }],
                            name: 'balance',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'swapped',
                            payable: false,
                            returns: { map: ['address', 'int'] },
                            stateful: false,
                        },
                        {
                            arguments: [],
                            name: 'allowances',
                            payable: false,
                            returns: 'FungibleTokenFull.allowances',
                            stateful: false,
                        },
                        {
                            arguments: [{ name: 'allowance_accounts', type: 'FungibleTokenFull.allowance_accounts' }],
                            name: 'allowance',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [{ name: 'from_account', type: 'address' }],
                            name: 'allowance_for_caller',
                            payable: false,
                            returns: { option: ['int'] },
                            stateful: false,
                        },
                        {
                            arguments: [
                                { name: 'from_account', type: 'address' },
                                { name: 'to_account', type: 'address' },
                                { name: 'value', type: 'int' },
                            ],
                            name: 'transfer_allowance',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: 'for_account', type: 'address' },
                                { name: 'value', type: 'int' },
                            ],
                            name: 'create_allowance',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: 'for_account', type: 'address' },
                                { name: 'value_change', type: 'int' },
                            ],
                            name: 'change_allowance',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [{ name: 'for_account', type: 'address' }],
                            name: 'reset_allowance',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: 'to_account', type: 'address' },
                                { name: 'value', type: 'int' },
                            ],
                            name: 'transfer',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [{ name: 'value', type: 'int' }],
                            name: 'burn',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        {
                            arguments: [
                                { name: 'account', type: 'address' },
                                { name: 'value', type: 'int' },
                            ],
                            name: 'mint',
                            payable: false,
                            returns: { tuple: [] },
                            stateful: true,
                        },
                        { arguments: [], name: 'swap', payable: false, returns: { tuple: [] }, stateful: true },
                        {
                            arguments: [{ name: 'account', type: 'address' }],
                            name: 'check_swap',
                            payable: false,
                            returns: 'int',
                            stateful: true,
                        },
                    ],
                    kind: 'contract_main',
                    name: 'FungibleTokenFull',
                    payable: false,
                    state: {
                        record: [
                            { name: 'owner', type: 'address' },
                            { name: 'total_supply', type: 'int' },
                            { name: 'balances', type: 'FungibleTokenFull.balances' },
                            { name: 'meta_info', type: 'FungibleTokenFull.meta_info' },
                            { name: 'allowances', type: 'FungibleTokenFull.allowances' },
                            { name: 'swapped', type: { map: ['address', 'int'] } },
                        ],
                    },
                    typedefs: [
                        {
                            name: 'meta_info',
                            typedef: {
                                record: [
                                    { name: 'name', type: 'string' },
                                    { name: 'symbol', type: 'string' },
                                    { name: 'decimals', type: 'int' },
                                ],
                            },
                            vars: [],
                        },
                        {
                            name: 'allowance_accounts',
                            typedef: {
                                record: [
                                    { name: 'from_account', type: 'address' },
                                    { name: 'for_account', type: 'address' },
                                ],
                            },
                            vars: [],
                        },
                        { name: 'balances', typedef: { map: ['address', 'int'] }, vars: [] },
                        {
                            name: 'allowances',
                            typedef: { map: ['FungibleTokenFull.allowance_accounts', 'int'] },
                            vars: [],
                        },
                    ],
                },
            },
        ],
    },
    // [Network.Ethereum]: {
    //     network: 'custom',
    //     ethChainId: '0x5',
    //     rpc: 'https://tezos-ghostnet-node-1.diamond.papers.tech',
    //     tezos_bridge: 'KT1AyXoM57cyXv8yZLn4nBNzVSmCJKMtuEdf',
    //     tezos_crowdfunding: 'KT1RUuZ1D8UZdY59cLjbC2GCCqP4HUvDeiix',
    //     tezos_validator: 'KT1QfWxeYitE4NXvC4caBJpwimzxZygqPJ9F',
    //     tezos_state_aggregator: 'KT1B8F7BhA2EeGQvPFpaVStd99ZDSzwrAcBL',
    //     evm_bridge: '0x945BEeA0C9C8052764e8Ef54a571386Cd1027BF1',
    //     evm_crowdfunding: '0x79a20860c063a70EB483f5b6fb70b9CaDb022729',
    //     evm_validator: '0xE258F751a56343b722263cbF9Fdf3e71F1815cAA',
    //     tokenSymbol: 'GoerliETH',
    //     etherscan: 'https://goerli.etherscan.io',
    //     tzkt: 'https://ghostnet.tzkt.io',
    //     rpcUrls: ['https://rpc.ankr.com/eth_goerli'],
    // },
};

export default Constants;
