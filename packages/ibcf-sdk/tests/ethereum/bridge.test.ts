import BigNumber from 'bignumber.js';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { ethers } from 'ethers';

import * as IBCF from '../../src';
import { Override } from '../utils';

describe('Ethereum > Bridge', () => {
    const host = 'http://mocked_rpc.localhost';
    const server = setupServer(...http_handlers(host, []));
    const provider = new ethers.providers.JsonRpcProvider(host);

    beforeAll(function () {
        server.listen();
    });

    afterAll(function () {
        server.close();
    });

    it('getAssetAddress', async () => {
        const overrides = [
            {
                method: 'eth_getStorageAt',
                response: {
                    result: '0x000000000000000000000000bae1aa092d2035f0eac4f35b26d4743e6f896ee4',
                },
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        const address = await IBCF.Ethereum.Contracts.Bridge.getAssetAddress(
            provider,
            '0xF8D0dcb8F3Af348586360971b3561B3b139a2929',
        );

        expect(address).toEqual('0xbae1aa092d2035f0eac4f35b26d4743e6f896ee4');
    });

    it('getWraps', async () => {
        const overrides = [
            {
                method: 'eth_getLogs',
                response: {
                    result: [
                        {
                            address: '0xbe0c32961da35928196f6bc912a3ed55d5d53f04',
                            blockHash: '0x409698515a5babb5e611341b67302ef80c31bdda958dfbc9a7626c57fd01ef4c',
                            blockNumber: '0x79ffa0',
                            data: '0x0000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000001c050a0000001600006b82198cb179e8306c1bedd08f12dc863f32888600000000',
                            logIndex: '0x1c',
                            removed: false,
                            topics: ['0xe86158b061920473e947f9d71db5734b884098902707f967f7ede6fadf1fa19c'],
                            transactionHash: '0xc0f7a7f596d34a6a6a189528b2c0be3b5f9433cec60658f37f979e29b144c45d',
                            transactionIndex: '0x10',
                        },
                        {
                            address: '0xbe0c32961da35928196f6bc912a3ed55d5d53f04',
                            blockHash: '0xcf4b5a297d4d2cef6f87d014abb68d98b0096eef730860a23797744bee944908',
                            blockNumber: '0x7a0ead',
                            data: '0x000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001c050a0000001600006b82198cb179e8306c1bedd08f12dc863f32888600000000',
                            logIndex: '0x2c',
                            removed: false,
                            topics: ['0xe86158b061920473e947f9d71db5734b884098902707f967f7ede6fadf1fa19c'],
                            transactionHash: '0xaf5f8b14cec5f0c5c596732857367230b05ce407665d65a67f710676ee33c11f',
                            transactionIndex: '0x12',
                        },
                    ],
                },
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        const address = await IBCF.Ethereum.Contracts.Bridge.getWraps(
            provider,
            '0xF8D0dcb8F3Af348586360971b3561B3b139a2929',
        );

        expect(address).toEqual([
            {
                address: 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
                amount: BigNumber(10),
                nonce: BigNumber(1),
            },
            {
                address: 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
                amount: BigNumber(2),
                nonce: BigNumber(2),
            },
        ]);
    });
});

const mock_RPC_method = (req: any, overrides: Override[]) => {
    for (const override of overrides) {
        if (req.body.method == override.method) {
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                ...override.response,
            };
        }
    }
    switch (req.body.method) {
        case 'eth_blockNumber':
            return {
                jsonrpc: '2.0',
                id: req.body.id,
                result: '0x7c318d',
            };
        case 'eth_getTransactionCount':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: '0xfc',
            };
        case 'net_version':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: '5',
            };
        case 'eth_gasPrice':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: '0xca7e6c08',
            };
        case 'eth_estimateGas':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: '0x5e38',
            };
        case 'eth_getBlockByNumber':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: {
                    baseFeePerGas: '0xc1721a6c',
                    difficulty: '0x0',
                    extraData: '0x',
                    gasLimit: '0x1c9c380',
                    gasUsed: '0x2e36a2',
                    hash: '0x50e1c7318fd810bde6a7738c213b8e41ac77a8716050fabfc8485600edd0a23f',
                    logsBloom:
                        '0x0030040000241008000020c480400000000a020000020802001148008840010c1024000402008200120041000080000808850000808082820004020483e0244080000020243000809808400818000064000880110384120000010114808000004221100026000aa006c1400084002d1001000202000a08082801181080010099000000a16010000080444004000001020224040104000008c14000413042004102094800000d1088000008460603080a012400011806800030102802012008010860402210000800180001020203201001001024040450100383002c000830008816a92c0000860a1008018800004102000130c8000200400248000008001001',
                    miner: '0xf36f155486299ecaff2d4f5160ed5114c1f66000',
                    mixHash: '0x2c34bf7b683f3541d3226e6d68db967430ccc4849f485b9d84194fd7aaba1c16',
                    nonce: '0x0000000000000000',
                    number: '0x7c3145',
                    parentHash: '0x426437fae3ea3bbd8dad9743289601d4869b926331751af371e6e1234ad9b3f5',
                    receiptsRoot: '0x82f4874321301be9d3978eba557566ebeb4185208334c6d9d4bcfa41222b1114',
                    sha3Uncles: '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
                    size: '0x1d94',
                    stateRoot: '0xae7b8c08a97c2b7fc73342863f53d30d2f265c48897958eafb5ae56149e46a7b',
                    timestamp: '0x639afb24',
                    totalDifficulty: '0xa4a470',
                    transactions: [
                        '0x25795a1423bb1a1dc2c3125c751f0c492ef1d7cf27918429eae9b77fa60c6c8c',
                        '0xbebae9d4a3713655c63e0d213a090f97c75f24417af55e573ecefac4ff97f2a6',
                        '0x2654845443270309431af43c9b70fb1fabd60d3f7ed8d9e2c0f673adc65082d7',
                        '0xe0864c831e88582ccd93ef2ba8019759b18e8c72fba06cfb9526fa023aefa7a2',
                        '0xac4ce3018484ad8e234994687cfd59cfdc8d67e4f0f1d34c3725b440aee601ef',
                        '0x25e4982fc2b428fdbc43d57882c5d977c6d66b01b92a2d1cd034d4514012c295',
                        '0x194cfcdf355f7a3f649e3c8c4403ce5ee8907c232b3d54c2505aff206c0421e7',
                        '0xfcd5befaabf48b5d1706d8f92b0cf752d85722007ce3bfdc17d995f981ce097f',
                        '0xa7569dfb250f182137762ee689449d28f72f5fd55137226a0fe740256d6459f5',
                        '0xafa8c28b175a7af6adde12741a73fe97bd21494a31d1361c52427e4088c957f7',
                        '0x34f1baa8005e17fa6a7adcbbcfa59470f3750137d94d8312fbe7754913b26622',
                        '0xc6058396862e9098cf3fd827ae72b6ea9be1a9e89123f2f1d120485bee4cef3d',
                        '0x4ab5de2712904f87e3f02fd3cb7e799df7f72fe1195b9acbb26161b586ad38e9',
                        '0xdebad1c238c8147de29e874a824253577aff9209f84468882c94c4373a3f3984',
                        '0x8303151343723315b08ef8b3390c8b9a8b381116dd29387d61e943b1aa7d6387',
                        '0xd8e25b25b28695eb94466c7f4e632c6d10d5f76b2daf657bb31f69fb448f2d96',
                        '0x48b9669f4778911361e7fdf6164ab6623bc2fbf571e005eb5e8859243f5b6ed9',
                        '0xdcec2a5e175fb3c6353aa8aa682ba947f3cf1508f1cfbebd661c1e6afbc6d86f',
                        '0x307a378420a3b6e7eb5cfdf2e6a1dbd7f66ad650647e7483b94cc215321e5a6e',
                        '0x5f53af722d687f703fd990241bfff8c1892b12f261b060bff0782911d4d46fe2',
                        '0x5f7c5169bbf57a2a55b04a55288aeb958a5baeb5ddaea7d260909695398d7b99',
                        '0xd9ebae9570ad02110a7f6dae4a922c2aa5a8cf07dfd0ad3f330658bc94997f84',
                        '0x85fce55573b091400fa44b4b00c48d85439c643497f8c22fee9578b71a31ed63',
                        '0xfaa8a243ab8115eee26d93c32681368e84b4a8222efa382be5c48638e62ab686',
                        '0x1cdee1cd14b9a1be3b5e8fbe93008c5ec3fda3ce3be21954e0275998df658828',
                    ],
                    transactionsRoot: '0x03e497d23aad8d0048752d41975daf1330c034e76cd60d6f4c265fc99c854b42',
                    uncles: [],
                },
            };
        case 'eth_chainId':
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                result: '0x5',
            };
    }

    console.error('The following request needs to be mocked:', JSON.stringify(req.body));
    throw new Error(`Method ${req.body.method} needs to be mocked.`);
};

function http_handlers(url: string, overrides: Override[]) {
    return [
        rest.post(`${url}/`, async (req, res, ctx) => {
            return res(ctx.json(mock_RPC_method(req, overrides)));
        }),
    ];
}
