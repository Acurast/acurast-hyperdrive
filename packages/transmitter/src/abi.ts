export const ibfc_client_abi: any = [
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
        name: 'ping',
        outputs: [],
        stateMutability: 'nonpayable',
        type: 'function',
    },
];
