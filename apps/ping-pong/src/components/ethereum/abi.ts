const ibfc_client_abi: any = [
    {
        inputs: [
            {
                internalType: 'address',
                name: '_validator_address',
                type: 'address',
            },
            {
                internalType: 'bytes',
                name: 'source',
                type: 'bytes',
            },
        ],
        stateMutability: 'nonpayable',
        type: 'constructor',
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
        name: 'confirm_ping',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
    {
        inputs: [],
        name: 'pong',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
    {
        inputs: [
            {
                internalType: 'string',
                name: '_counter',
                type: 'string',
            },
        ],
        name: 'set_counter',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
    {
        inputs: [
            {
                internalType: 'bytes',
                name: 'source',
                type: 'bytes',
            },
        ],
        name: 'set_tezos_source',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
];

export default ibfc_client_abi;
