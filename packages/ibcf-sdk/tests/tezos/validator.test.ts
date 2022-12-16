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
const contract = 'KT1VYAacqwcXQ8W1fZ4pApx5JwR6Si4nn1sX';

describe('Tezos > Validator', () => {
    const server = setupServer(...http_handlers('http://mocked_rpc.localhost'));
    const tezos_sdk = new TezosToolkit('http://mocked_rpc.localhost');

    beforeAll(function () {
        server.listen();
    });

    afterAll(function () {
        server.close();
    });

    it('getStorage', async () => {
        const contractStorage = await IBCF.Tezos.Contracts.Validator.getStorage(tezos_sdk, contract);

        expect(contractStorage.current_snapshot).toEqual(new BigNumber(1));
    });

    describe('Entrypoints', () => {
        it('submit_block_state_root', async () => {
            const result = await IBCF.Tezos.Contracts.Validator.submit_block_state_root(
                tezos_sdk,
                contract,
                1,
                '0x0000',
            );
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
            return res(ctx.json(contractEntrypointsResponse));
        }),
        rest.get(`${url}/chains/main/blocks/head/context/contracts/${contract}/script`, async (req, res, ctx) => {
            return res(ctx.json(contractScriptResponse));
        }),

        rest.post(`${url}/injection/operation`, async (req, res, ctx) => {
            return res(ctx.text('opLyi4ZBGDf3pb4A8eLkyouiFqNVgQ8X59ZStMesgYsHrQSLMGQ'));
        }),
    ];
}
