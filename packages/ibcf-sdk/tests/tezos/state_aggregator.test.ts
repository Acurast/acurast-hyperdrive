import BigNumber from 'bignumber.js';
import { TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

import blockHeader from './data/block_header.json';
import protocolConstants from './data/constants.json';
import contractResponse from './data/state_aggregator.contract.json';
import contractScriptResponse from './data/state_aggregator.script.json';
import entrypoints from './data/state_aggregator.entrypoints.json';
import * as IBCF from '../../src';

const signer_address = 'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd';
const contract = 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd';

describe('Tezos > State Aggregator', () => {
    const server = setupServer(...http_handlers('http://mocked_rpc.localhost'));
    const tezos_sdk = new TezosToolkit('http://mocked_rpc.localhost');

    beforeAll(function () {
        server.listen();
    });

    afterAll(function () {
        server.close();
    });

    it('getStorage', async () => {
        const contractStorage = await IBCF.Tezos.Contracts.StateAggregator.getStorage(tezos_sdk, contract);
        // console.log(contractStorage);
        expect(contractStorage.snapshot_counter).toEqual(new BigNumber(3));
        expect(contractStorage.merkle_tree.root).toEqual(
            'a45c3c2bb154f7ee78a28d825c2b77d283a3d57acc5e979876971d0e8d2b7dbb',
        );
    });

    describe('Entrypoints', () => {
        it('snapshot', async () => {
            tezos_sdk.setSignerProvider(
                await InMemorySigner.fromSecretKey(
                    'edskS8xUePnvXXp3XHjYkDBBKDRwigGF95uHtJzDakV74azm9y6KHvkw4gLjPUvenWiY7H9xRQN729ipPutLVLiHXHMYfaf9hS',
                ),
            );

            const result = await IBCF.Tezos.Contracts.StateAggregator.snapshot(tezos_sdk, contract);
            expect(result.hash).toEqual('opLyi4ZBGDf3pb4A8eLkyouiFqNVgQ8X59ZStMesgYsHrQSLMGQ');
        });

        // it('getProof', async () => {
        //     const contract = 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd';
        //     server.on({
        //         method: '*',
        //         path: `*`,
        //         reply: {
        //             status: 200,
        //             headers: { 'content-type': 'application/json' },
        //             body: function (req: any) {
        //                 return '';
        //             },
        //         },
        //     });

        //     const tezos_sdk = new TezosToolkit('http://localhost:10000');

        //     const current_snapshot = await IBCF.Tezos.Contracts.StateAggregator.getProof(tezos_sdk, contract, '', '', '');

        //     // expect(current_snapshot).toEqual(new BigNumber(0));
    });
});

function http_handlers(url: string) {
    return [
        rest.get(`${url}/chains/main/blocks/head/protocols`, async (req, res, ctx) => {
            return res(
                ctx.json({
                    protocol: 'PtLimaPtLMwfNinJi9rCfDPWea8dFgTZ1MeJ9f1m2SRic6ayiwW',
                    next_protocol: 'PtLimaPtLMwfNinJi9rCfDPWea8dFgTZ1MeJ9f1m2SRic6ayiwW',
                }),
            );
        }),
        rest.get(`${url}/chains/main/chain_id`, async (req, res, ctx) => {
            return res(ctx.json('NetXnHfVqm9iesp'));
        }),
        rest.get(`${url}/chains/main/blocks/head~2/header`, async (req, res, ctx) => {
            return res(ctx.json(blockHeader));
        }),
        rest.get(
            `${url}/chains/main/blocks/head/context/contracts/${signer_address}/balance`,
            async (req, res, ctx) => {
                return res(ctx.json('324234324'));
            },
        ),
        rest.get(
            `${url}/chains/main/blocks/head/context/contracts/${signer_address}/manager_key`,
            async (req, res, ctx) => {
                return res(ctx.json('edpkuCoqz3RtxwpFfvmhrUwMv2yECB13hVTpvdFmHhbrEFCLogAb6Z'));
            },
        ),
        rest.get(`${url}/chains/main/blocks/head/context/constants`, async (req, res, ctx) => {
            return res(ctx.json(protocolConstants));
        }),
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${signer_address}`, async (req, res, ctx) => {
            return res(
                ctx.json({
                    balance: '999999060',
                    counter: '13764685',
                }),
            );
        }),
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${contract}`, async (req, res, ctx) => {
            return res(ctx.json(contractResponse));
        }),
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${contract}/entrypoints`, async (req, res, ctx) => {
            return res(ctx.json(entrypoints));
        }),
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${contract}/script`, async (req, res, ctx) => {
            return res(ctx.json(contractScriptResponse));
        }),

        rest.post(`${url}/injection/operation`, async (req, res, ctx) => {
            return res(ctx.text('opLyi4ZBGDf3pb4A8eLkyouiFqNVgQ8X59ZStMesgYsHrQSLMGQ'));
        }),
        rest.post(`${url}/chains/main/blocks/head/helpers/preapply/operations`, async (req, res, ctx) => {
            return res(
                ctx.json([
                    {
                        contents: [
                            {
                                kind: 'transaction',
                                source: 'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd',
                                fee: '561',
                                counter: '13764686',
                                gas_limit: '2551',
                                storage_limit: '0',
                                amount: '0',
                                destination: 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd',
                                parameters: {
                                    entrypoint: 'snapshot',
                                    value: {
                                        prim: 'Unit',
                                    },
                                },
                                metadata: {
                                    balance_updates: [
                                        {
                                            kind: 'contract',
                                            contract: 'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd',
                                            change: '-561',
                                            origin: 'block',
                                        },
                                        {
                                            kind: 'accumulator',
                                            category: 'block fees',
                                            change: '561',
                                            origin: 'block',
                                        },
                                    ],
                                    operation_result: {
                                        status: 'applied',
                                        storage: [
                                            {
                                                prim: 'Pair',
                                                args: [
                                                    {
                                                        bytes: '00006b82198cb179e8306c1bedd08f12dc863f328886',
                                                    },
                                                    {
                                                        prim: 'Pair',
                                                        args: [
                                                            {
                                                                int: '32',
                                                            },
                                                            {
                                                                int: '5',
                                                            },
                                                        ],
                                                    },
                                                ],
                                            },
                                            [
                                                [],
                                                {
                                                    bytes: '',
                                                },
                                                {
                                                    prim: 'Pair',
                                                    args: [
                                                        {
                                                            prim: 'Pair',
                                                            args: [
                                                                {
                                                                    int: '0',
                                                                },
                                                                {
                                                                    int: '0',
                                                                },
                                                            ],
                                                        },
                                                        {
                                                            bytes: '',
                                                        },
                                                    ],
                                                },
                                                [],
                                            ],
                                            {
                                                int: '7',
                                            },
                                            {
                                                int: '217639',
                                            },
                                            {
                                                int: '1667068',
                                            },
                                        ],
                                        consumed_milligas: '1450295',
                                        storage_size: '7954',
                                        lazy_storage_diff: [
                                            {
                                                kind: 'big_map',
                                                id: '217639',
                                                diff: {
                                                    action: 'update',
                                                    updates: [
                                                        {
                                                            key_hash:
                                                                'exprufunBN3FAVpZ21WXquoqiNyWB2PvYy1njkP4wHGtMexdKtcJEM',
                                                            key: {
                                                                int: '7',
                                                            },
                                                            value: {
                                                                int: '1667067',
                                                            },
                                                        },
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    internal_operation_results: [
                                        {
                                            kind: 'event',
                                            source: 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd',
                                            nonce: 0,
                                            type: {
                                                prim: 'pair',
                                                args: [
                                                    {
                                                        prim: 'nat',
                                                        annots: ['%level'],
                                                    },
                                                    {
                                                        prim: 'nat',
                                                        annots: ['%snapshot'],
                                                    },
                                                ],
                                            },
                                            tag: 'SNAPSHOT_FINALIZED',
                                            payload: {
                                                prim: 'Pair',
                                                args: [
                                                    {
                                                        int: '1667068',
                                                    },
                                                    {
                                                        int: '7',
                                                    },
                                                ],
                                            },
                                            result: {
                                                status: 'applied',
                                                consumed_milligas: '1000000',
                                            },
                                        },
                                    ],
                                },
                            },
                        ],
                        signature:
                            'edsigtiFyGJbLBBt1C6sn6Vg729kr6bWxAFTtWg2LwESbq9kLCfmoGYFW5xXuZTYQosqjKJEDDeB9ZWwhbpqNDjomqtvHSNV8F1',
                    },
                ]),
            );
        }),

        rest.post(`${url}/chains/main/blocks/head/helpers/scripts/run_operation`, async (req, res, ctx) => {
            return res(
                ctx.json({
                    contents: [
                        {
                            kind: 'transaction',
                            source: 'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd',
                            fee: '0',
                            counter: '13764686',
                            gas_limit: '1040000',
                            storage_limit: '60000',
                            amount: '0',
                            destination: 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd',
                            parameters: {
                                entrypoint: 'snapshot',
                                value: {
                                    prim: 'Unit',
                                },
                            },
                            metadata: {
                                operation_result: {
                                    status: 'applied',
                                    storage: [
                                        {
                                            prim: 'Pair',
                                            args: [
                                                {
                                                    bytes: '00006b82198cb179e8306c1bedd08f12dc863f328886',
                                                },
                                                {
                                                    prim: 'Pair',
                                                    args: [
                                                        {
                                                            int: '32',
                                                        },
                                                        {
                                                            int: '5',
                                                        },
                                                    ],
                                                },
                                            ],
                                        },
                                        [
                                            [],
                                            {
                                                bytes: '',
                                            },
                                            {
                                                prim: 'Pair',
                                                args: [
                                                    {
                                                        prim: 'Pair',
                                                        args: [
                                                            {
                                                                int: '0',
                                                            },
                                                            {
                                                                int: '0',
                                                            },
                                                        ],
                                                    },
                                                    {
                                                        bytes: '',
                                                    },
                                                ],
                                            },
                                            [],
                                        ],
                                        {
                                            int: '7',
                                        },
                                        {
                                            int: '217639',
                                        },
                                        {
                                            int: '1667063',
                                        },
                                    ],
                                    consumed_milligas: '1450295',
                                    storage_size: '7954',
                                    lazy_storage_diff: [
                                        {
                                            kind: 'big_map',
                                            id: '217639',
                                            diff: {
                                                action: 'update',
                                                updates: [
                                                    {
                                                        key_hash:
                                                            'exprufunBN3FAVpZ21WXquoqiNyWB2PvYy1njkP4wHGtMexdKtcJEM',
                                                        key: {
                                                            int: '7',
                                                        },
                                                        value: {
                                                            int: '1667062',
                                                        },
                                                    },
                                                ],
                                            },
                                        },
                                    ],
                                },
                                internal_operation_results: [
                                    {
                                        kind: 'event',
                                        source: 'KT1PgvJ629MCN99k9EKYTaWZJXB9zd5bzvzd',
                                        nonce: 0,
                                        type: {
                                            prim: 'pair',
                                            args: [
                                                {
                                                    prim: 'nat',
                                                    annots: ['%level'],
                                                },
                                                {
                                                    prim: 'nat',
                                                    annots: ['%snapshot'],
                                                },
                                            ],
                                        },
                                        tag: 'SNAPSHOT_FINALIZED',
                                        payload: {
                                            prim: 'Pair',
                                            args: [
                                                {
                                                    int: '1667063',
                                                },
                                                {
                                                    int: '7',
                                                },
                                            ],
                                        },
                                        result: {
                                            status: 'applied',
                                            consumed_milligas: '1000000',
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                    signature:
                        'edsigtkpiSSschcaCt9pUVrpNPf7TTcgvgDEDD6NCEHMy8NNQJCGnMfLZzYoQj74yLjo9wx6MPVV29CvVzgi7qEcEUok3k7AuMg',
                }),
            );
        }),
    ];
}
