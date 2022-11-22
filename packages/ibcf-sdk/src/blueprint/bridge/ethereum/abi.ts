const abi = [
    {
        inputs: [
            {
                internalType: 'contract IBCF_Validator',
                name: '_validator',
                type: 'address',
            },
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
                name: 'nonce',
                type: 'uint256',
            },
        ],
        name: 'Unwrap',
        type: 'event',
    },
    {
        anonymous: false,
        inputs: [
            {
                indexed: false,
                internalType: 'bytes',
                name: 'destination',
                type: 'bytes',
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
        name: 'Wrap',
        type: 'event',
    },
    {
        inputs: [
            {
                internalType: 'bytes',
                name: '_tezos_bridge_address',
                type: 'bytes',
            },
        ],
        name: 'set_tezos_bridge_address',
        outputs: [
            {
                internalType: 'bool',
                name: '',
                type: 'bool',
            },
        ],
        stateMutability: 'nonpayable',
        type: 'function',
    },
    {
        inputs: [
            {
                internalType: 'bytes',
                name: 'target_address',
                type: 'bytes',
            },
            {
                internalType: 'uint256',
                name: 'amount',
                type: 'uint256',
            },
        ],
        name: 'wrap',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
    {
        inputs: [
            {
                internalType: 'uint256',
                name: 'block_level',
                type: 'uint256',
            },
            {
                internalType: 'bytes32',
                name: 'merkle_root',
                type: 'bytes32',
            },
            {
                internalType: 'bytes',
                name: 'key',
                type: 'bytes',
            },
            {
                internalType: 'bytes',
                name: 'value',
                type: 'bytes',
            },
            {
                internalType: 'bytes32[2][]',
                name: 'proof',
                type: 'bytes32[2][]',
            },
            {
                internalType: 'address[]',
                name: '_signers',
                type: 'address[]',
            },
            {
                internalType: 'uint256[2][]',
                name: 'signatures',
                type: 'uint256[2][]',
            },
        ],
        name: 'unwrap',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
];

export default abi;
