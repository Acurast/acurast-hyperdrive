import BigNumber from 'bignumber.js';
import { TezosToolkit } from '@taquito/taquito';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

import blockHeader from './data/block_header.json';
import protocolConstants from './data/constants.json';
import contractResponse from './data/validator.contract.json';
import contractScriptResponse from './data/validator.script.json';
import contractEntrypointsResponse from './data/validator.entrypoints.json';
import * as IBCF from '../../src';

const signer_address = 'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd';
const contractAddress = 'KT1VYAacqwcXQ8W1fZ4pApx5JwR6Si4nn1sX';

describe('Tezos > Validator', () => {
    const server = setupServer(...http_handlers('http://mocked_rpc.localhost'));
    const tezos_sdk = new TezosToolkit('http://mocked_rpc.localhost');
    const contract = new IBCF.Tezos.Contracts.Validator.Contract(tezos_sdk, contractAddress);

    beforeAll(function () {
        server.listen();
    });

    afterAll(function () {
        server.close();
    });

    it('getStorage', async () => {
        const contractStorage = await contract.getStorage();

        expect(contractStorage.config.administrator).toEqual('tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd');
        expect(contractStorage.config.minimum_endorsements.toNumber()).toEqual(1);
        expect(contractStorage.config.snapshot_interval.toNumber()).toEqual(10);
        expect(contractStorage.config.validators).toEqual([
            'tz1XvqmBUa7SkUFRHSygUZsxMwh7i8GpV7iB',
            'tz1YGTtd1hqGYTYKtcWSXYKSgCj5hvjaTPVd',
            'tz1aBNXcSKfWE7aujp2Twa7V7Beua2fjhri3',
            'tz3LXMyngf729xwrmwV9yUv7jRwmuNvYX3JR',
        ]);
        expect(contractStorage.current_snapshot).toEqual(new BigNumber(8343650));
        expect(contractStorage.history.length).toEqual(contractStorage.config.history_length.toNumber());
    });

    it('latestSnapshot', async () => {
        const latestSnapshot = await contract.latestSnapshot();

        expect(latestSnapshot).toEqual({
            block_number: 8343640,
            merkle_root: '59f8fcb141d9e750d4e380c3630b7462b9533b8ab96d2fd79cd37ff21d8eb4a8',
        });
    });

    describe('Entrypoints', () => {
        it('submit_block_state_root', async () => {
            const result = await contract.submitBlockStateRoot(1, '0x0000');
            expect(result.toTransferParams()).toEqual({
                amount: 0,
                fee: undefined,
                gasLimit: undefined,
                mutez: false,
                parameter: {
                    entrypoint: 'submit_block_state_root',
                    value: { prim: 'Pair', args: [{ int: '1' }, { bytes: '0000' }] },
                },
                source: undefined,
                storageLimit: undefined,
                to: 'KT1VYAacqwcXQ8W1fZ4pApx5JwR6Si4nn1sX',
            });
        });
    });
});

function http_handlers(url: string) {
    return [
        rest.post(`${url}/chains/main/blocks/head/helpers/scripts/pack_data`, async (req, res, ctx) => {
            return res(
                ctx.json({
                    packed: '050098c1fa07',
                    gas: 'unaccounted',
                }),
            );
        }),
        rest.get(
            `${url}/chains/main/blocks/head/context/big_maps/235755/expruWT9HPZspb6HMuAC4DEVyWDpGfVA1C4ARneriPdqZB93WPCnqp`,
            async (req, res, ctx) => {
                return res(
                    ctx.json([
                        {
                            prim: 'Elt',
                            args: [
                                {
                                    string: 'tz1XvqmBUa7SkUFRHSygUZsxMwh7i8GpV7iB',
                                },
                                {
                                    bytes: '59f8fcb141d9e750d4e380c3630b7462b9533b8ab96d2fd79cd37ff21d8eb4a8',
                                },
                            ],
                        },
                    ]),
                );
            },
        ),
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
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${contractAddress}`, async (req, res, ctx) => {
            return res(ctx.json(contractResponse));
        }),
        rest.get(
            `${url}/chains/main/blocks/head/context/contracts/${contractAddress}/entrypoints`,
            async (req, res, ctx) => {
                return res(ctx.json(contractEntrypointsResponse));
            },
        ),
        rest.get(
            `${url}/chains/main/blocks/head/context/contracts/${contractAddress}/script`,
            async (req, res, ctx) => {
                return res(ctx.json(contractScriptResponse));
            },
        ),

        rest.post(`${url}/injection/operation`, async (req, res, ctx) => {
            return res(ctx.text('opLyi4ZBGDf3pb4A8eLkyouiFqNVgQ8X59ZStMesgYsHrQSLMGQ'));
        }),
    ];
}
