import BigNumber from 'bignumber.js';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { ethers } from 'ethers';

import * as IBCF from '../../src';
import { Override } from '../utils';

describe('Ethereum > Bridge', () => {
    const contractAddress = '0xF8D0dcb8F3Af348586360971b3561B3b139a2929';
    const host = 'http://mocked_rpc.localhost';
    const server = setupServer(...http_handlers(host, []));
    const provider = new ethers.providers.JsonRpcProvider(host);
    const wallet = new ethers.Wallet('0x1111111111111111111111111111111111111111111111111111111111111111', provider);
    const contract = new IBCF.Ethereum.Contracts.Bridge.Contract(wallet, contractAddress);

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
                responses: [
                    {
                        result: '0x000000000000000000000000bae1aa092d2035f0eac4f35b26d4743e6f896ee4',
                    },
                ],
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        const address = await contract.getAssetAddress();

        expect(address).toEqual('0xbae1aa092d2035f0eac4f35b26d4743e6f896ee4');
    });

    it('unwrapProcessed', async () => {
        let overrides = [
            {
                method: 'eth_getStorageAt',
                responses: [
                    {
                        result: '0x0000000000000000000000000000000000000000000000000000000000000001',
                    },
                ],
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        expect(await contract.unwrapProcessed(1)).toEqual(true);

        overrides = [
            {
                method: 'eth_getStorageAt',
                responses: [
                    {
                        result: '0x0000000000000000000000000000000000000000000000000000000000000000',
                    },
                ],
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        expect(await contract.unwrapProcessed(1)).toEqual(false);
    });

    it('getWraps', async () => {
        const overrides = [
            {
                method: 'eth_getLogs',
                responses: [
                    {
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
                ],
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        const address = await contract.getWraps();

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

    it('generateWrapProof', async () => {
        const overrides = [
            {
                method: 'eth_getProof',
                responses: [
                    {
                        result: {
                            accountProof: [
                                '0xf90211a080a7df79a291358fde6b03b441c46a41ce9a670d77f10165d6a802b1c97aef13a0d2daf22d3d772336ea8a833760360bc3c3c2a188852d2a2bb43978e9b162d7f7a05ce6b7233d2c09087b6e53b2438a26b751d961ff7598381f1dda0acfbf50b386a0a40448cf34702c280f3550f7caa8a7338895a49eda8c610beead9dc954f34aa1a03eca34b56c722e4531b67f810bf6a00b2f2c10469c110625df2933d739c60e40a08780afbad6011664e14532f11c0cb96d5e3c14ce4222ec8baef4d00771abaae2a0f2bf56c1f0798e28500d2626c0ce38dfed24a655f22da4c66d78eb5d76232240a028f2fc7eca5814ba862047b09f9353a9afae6e47873ebf98f7ed51aa68a5e114a03959fe2ebb6f47d2bc95d343f8a8aa7cb951b1a76b72a4c786f41948ba248a67a0e6be6942477e602945adede5263357c48138b6eb907238afce09bbfec75f7473a024713bbf3c62f9b3c11904c7d07c7c7d783c42be41fad96c4f651cc70a5ee53fa0eb14f8c063eb604ace9697375795433ccb6b11b4c9d022fccff180d229f3e2f6a004e5d44adfd6ec84e4516ba2519a8e21d0fd75aed327c90550e974ec6a1316e1a0550e05d69b63767ad6d6e4ae7183b23b7f97e9030dbd21078ad851f9285960e4a017ccc16894bdae6dce34fb09d7f21ec8cfde88ccbed89c26c6612adf16dba825a02b4477ef618e83091efaa4b59f2d81f16902062ee29bb169e4f23b74d0eb2e9a80',
                                '0xf90211a07e045193beaa121e9bd4f7a1aa88ef723722be6b01a7905eabb29bf7954f9f90a025a7579522e9ef773d9089a7e89c7ab15b512119e33bbe68b84e8cd1d33f92b0a0c80d5f5eead097a22f5669a6a09b1b8dd4e77809879ba82bc10c2912dfba9928a0fad6f0c762b324940a2ed88daf34c986a5a08f402e17c700dd23ddccb3b09805a05716ed3cd3a97f060e4e6889de2de9dabb4c48e381855b200ff87a6abd743a52a018e3254b08479a594865115e5bc72b5e74dd4d9e46ca583d9d4bf1d06e7064bba0828fe97a9d75b1b50551eadd5a5b9c20955f81aadb0926ad18512931b6aa8e6ba0d0085e7ebd36c7be94d5dc2ddc8968627b302329af538cd638c8750103b69817a05f93c6c39ae1cc916e9165bda3a4c420aff78652f32b24b07cea821a4ad24327a0034a0eaec5d7b986f8f56c558aaed1a1b8ff1136503dfdd7985addc748428057a08a358e2a3d771f17aad093f61e7bb8305872dd5092ceb615e610c9dd330b693ca0d3bc581e4e124a4bb64b6314f5bdec64faebaf48477508de739d2e3e561cf2a0a06158da0e62a6f34335ac2294bc09d95870ed7ff6827dc96ba24491c282f98bfca023ca1a69e2132545ad89d1a412d2afce25f3ca8d09062109bb03bae117ebdfd8a01e808d97e57f82fe8ca3ef7766a5b49a47635b6930732d68d52477c48b5d1b9ea0b623494d96c239befae49cea940d8000c73bf8140f94d8f9c31afdb4b8fdaf1180',
                                '0xf90211a03e7c2180f3cd6d4a75b90d8430029b6e80cee6c94075fc21783e8b72ad199a18a0b47d1c7809fa4d309ddc450c0df23311ad395d8d45a0cd01a84caa68dbbdd503a0d5c6edfddcaaa0a96b24bee6a39149c5ff1fc5c27ac1c97176c2bca3ed9c2880a038aaf16da01eaa865dd28d5714f89ff2fbdf32bc1174c28cbdd1734543d4488aa0ae61e63288db71244b4e76642dd7dfddbbbcd543f7afc6658bbd6cc18ff3a0aaa0c123bfef78683e542eff06e0693e896d945963b0d025c10c311665c478a9a7baa06a96b9244d18763826b2606b84c8b441a531c1a47ce00b285f253a9780d992afa017ac4add3466d235be7cb10da0ffee5d3b02da28517d97bcfcbb252d9b01dde3a04cef6b08eaf66300f0acd6c6a2c65fb5f01aa564f333fdcb3200944f7ffd33bea055faf22be41a521b89dcdd25244d91561f99a1619bc26029adcefdcf37eb5a27a0929ed73c787cf96100b5763d6271986e291a1644868f76dd7d2c0a1362aa6550a090db87ceeb862c49db931ff2eef3f9f5dd0c39eeff6f59ab7dac0695bf084cd3a0ae7bccf15479e634d780683390efb161c96740ff8daf011f3688d2aac33d2cfea03bf17d379a6df590c938c2e69b1ae5a713c7e34fdf1825620b309896f3df676ea0cb970b5f5f5ba1e527bfe82689e2203cb07ddcdc7b0d56538bf296d7ed9eb544a059854c3511ecdca1e5727a40679bbc88a9d453776d155dd5e658707aca3639e580',
                                '0xf90211a011be8b5fb88ff7aa28c09cfafcba5a9266a8c6ab7415fec23be9b05e25914549a0090152d2cf7d3ea1cc4ffc10e726be551582387d2705f7c0a6b060ed445d9395a097966335815eecc392d96201c3736c2be7b5c77bd5b800a0c5e19d7703cba974a0a946285bc5898dfb4f83f664accf62864a4e6de047793516b5c6a35f2d38ed43a0e87827afee8ac50223c416f6090f3cfa6c096ad6ecef4be68b776039c6b9e5eba003feda244ae7754eed3f49f073a4b6002d3a00be33137083bce980f691d37ecaa074bf7672ca48de112c4bee7d5246702b6861d21d6e83e5ea38e147fd192bb5c0a0e312120c11fcca90e1f28b26494edb9221523028009bb0f287eff7ed30f98ba3a0bcf3481d30b726e2596b54f0c897000e09e1eecdf3dd337a43f329b4156fd23ca0ef85927f73fb6ea534102b0b565b80c4dd9554232268e56f4ef37597578d456ba09774de1ca83837b2d5cdf15f0b4ef5c4be94f1d544c6061e8f88338f4a42b704a0b9da09c38a401041ce317cabfc29ac87c4a13ea4864b0dc6381c39ff991474a1a0d0e75d69f905de8490006eb3ce0fafb1fa2b1362d0c3937fa76f6c8ca8f843aca07e3f69b7acf34125a0152a2b784eb31fe693013c56f64af2bafda107d8377e95a056b76fc9b3ef6d9239a68e38dadebdf53a187605d4a52978ce8ed5c6d9318d87a0b76756a9cd39fba364a57431ab676c93d732188c865f5a630e0cd49b70d12ea180',
                                '0xf90211a0165b4d3bd40cffa63274318510d3f066412b83081630aed6c7994c7697b2f809a04c14d35668a1b86c9931d6d15a8967d960faf5ae6b99ad869a981f512035b205a027590984c4ef7c869efd1102e84a359da86182e751351435233b9b2c450e558ca07b4d3e5387914a8b96722b44259126cb9179b119f0898af5bc9edbc6e11083aaa0dc65fdbd0b217c892ef11fcaf0aa8fd425866cc48558231a30c5a8ddedd04e2ea02e33b12d13b94415c7456211b84fbbfcd2fbf96b35dfbd897e5458f63f597871a0b3a1f07aa206966bb128d308aac69e9c04d8079189e923687e00b09572457ae7a073813e0b0e1e057f716fa315d4657b5f41fbde0016e32a28cfe30eb16e21a8eea08497fe87cabf32c658275ba1621710163ef3a4520e10510043f27f3f082d9f8aa068e03504317fb94e37538a82a0408ed1ea3c1160b22b815bdfc62f091cb7497da0a422a857fca584893c3844d44ea4376400f74ccf4d9ffb32fc063274ba807769a0af490d10258a0f07b1005f363d3b1d91466c49fc4b25a0aabd8b47c9d1caa925a0ca214358f3d132b18ca4cffa730f80b74fc96b0826d12ff4f5fee170226e9568a0f1bbc518f71f588105abb80843439f9e8a947664939395d46e6e31df29c58d7fa05843dd8e31cae42aed665b567d004e9898d525a5938ce3bb8ffc8b94b600004ca00958013dac4df62af26c61fec70b6c2b000fb6e121a3c5156664865b30dd46ac80',
                                '0xf901f1a08f4eb7b5d821b9b24551e41128d8a4b3de653abd8a8d80741d32fc5d0cd57d93a00c5060efad572388ce9afaf91488e090d0e7265f5b2a819bc4f45f4491363ee9a0c49ea321de5311eb4467ea7401149b298c861535c3689cef40d504bea6c93aaea00f6c0408af7cb6fe4ee3449fae29331cabff8cc7f9c7ffd1a875e25ef03bcb41a0c96efbd3963092ad575535fff6174a3107e14ecae1fbae49f02300deca62d218a07b63248c4f059ac7e64505f79569cd7a4b86f44a62356285fa272d844b62dd8ca028bfdd748f96b003410fb20d35e48538bb10363d1c0c41d7b8384fb3215b9489a0b76bd898a726d05d0b1f4c994876eab9f91d54a8f386ed88d9b64e1549309e9ca0e12a9c1ff8f987cf534fab733e14915eb119016f094bcf9d02fec3bd323a68cfa0669ec1a83c35d5d3f2ac1ae62bd973afb2881c32db0760bdb243a703885ebf07a080aa95e8dffb9a24f5c1681d7e0cad7b3fde41cf9c2b9a3ed6055024531477f6a07f55683c3947db1f7b825e2b0d6ee1476da95370c879b6405cd5193a0efcb30aa02360e93621045f22c2dd90218af1a0790eed0cd26bc816e858eb0c35f087b7f580a045053947b439f62f2b16f41e83eb4c1873b9be7ce5362acf122a1535b8d5a103a06ee606f1e9703b8d864f712cce8d37179a8e798637903e31806554f72d55475480',
                                '0xf85180808080808080a05e95c78f78ec590c001737ada0b4a710ca4ad4039c6e128a81073f176fb4a3e9a0ead00c8f78dcf1931065ec87f9c8f29ec3044bccf0e94f2474916cddf040bb948080808080808080',
                                '0xf8669d3c95b4f82d864d940e697d372de64b7397550b1654737dc867833cfde2b846f8440180a087f48fbdefc1df71433106c8d8839989adf1c619c9546780891eabbac3c92af4a0093d9d09c70d7e96055070ed693b893307aa38ee0421e31ccaef4398cd25c150',
                            ],
                            address: '0xf8d0dcb8f3af348586360971b3561b3b139a2929',
                            balance: '0x0',
                            codeHash: '0x093d9d09c70d7e96055070ed693b893307aa38ee0421e31ccaef4398cd25c150',
                            nonce: '0x1',
                            storageHash: '0x87f48fbdefc1df71433106c8d8839989adf1c619c9546780891eabbac3c92af4',
                            storageProof: [
                                {
                                    key: '0x1471eb6eb2c5e789fc3de43f8ce62938c7d1836ec861730447e2ada8fd81017b',
                                    proof: [
                                        '0xf8b18080a049fbc0cfd59d5134b4866623fb6452232b73866cc174471272924657d54c57ff8080a0afc054367ea8d102e64acfc11cabd5c627968d856ee2a092aa1100880181c8b78080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a087e2fb4619bfe78f82e422f348334ca76d290f828c5d459612beb6c61caa4e0da01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c380808080',
                                        '0xf843a03ab3c568e6b9e23c87101e15642000038e2a634c0eba9355f868407d119483c2a1a0050a0000001600008a8584be3718453e78923713a6966202b05f99c600000038',
                                    ],
                                    value: '0x50a0000001600008a8584be3718453e78923713a6966202b05f99c600000038',
                                },
                                {
                                    key: '0x3e5fec24aa4dc4e5aee2e025e51e1392c72a2500577559fae9665c6d52bd6a31',
                                    proof: [
                                        '0xf8b18080a049fbc0cfd59d5134b4866623fb6452232b73866cc174471272924657d54c57ff8080a0afc054367ea8d102e64acfc11cabd5c627968d856ee2a092aa1100880181c8b78080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a087e2fb4619bfe78f82e422f348334ca76d290f828c5d459612beb6c61caa4e0da01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c380808080',
                                        '0xe2a030497882cf9008f7f796a89e5514a7b55bd96eab88ecb66aee4fb0a6fd34811c0a',
                                    ],
                                    value: '0xa',
                                },
                            ],
                        },
                    },
                ],
            },
        ];
        server.resetHandlers(...http_handlers(host, overrides));

        const address = await contract.generateWrapProof(
            '0000000000000000000000000000000000000000000000000000000000000001',
            8287100,
        );

        expect(address).toEqual({
            account_proof_rlp:
                '0xf90d13f90211a080a7df79a291358fde6b03b441c46a41ce9a670d77f10165d6a802b1c97aef13a0d2daf22d3d772336ea8a833760360bc3c3c2a188852d2a2bb43978e9b162d7f7a05ce6b7233d2c09087b6e53b2438a26b751d961ff7598381f1dda0acfbf50b386a0a40448cf34702c280f3550f7caa8a7338895a49eda8c610beead9dc954f34aa1a03eca34b56c722e4531b67f810bf6a00b2f2c10469c110625df2933d739c60e40a08780afbad6011664e14532f11c0cb96d5e3c14ce4222ec8baef4d00771abaae2a0f2bf56c1f0798e28500d2626c0ce38dfed24a655f22da4c66d78eb5d76232240a028f2fc7eca5814ba862047b09f9353a9afae6e47873ebf98f7ed51aa68a5e114a03959fe2ebb6f47d2bc95d343f8a8aa7cb951b1a76b72a4c786f41948ba248a67a0e6be6942477e602945adede5263357c48138b6eb907238afce09bbfec75f7473a024713bbf3c62f9b3c11904c7d07c7c7d783c42be41fad96c4f651cc70a5ee53fa0eb14f8c063eb604ace9697375795433ccb6b11b4c9d022fccff180d229f3e2f6a004e5d44adfd6ec84e4516ba2519a8e21d0fd75aed327c90550e974ec6a1316e1a0550e05d69b63767ad6d6e4ae7183b23b7f97e9030dbd21078ad851f9285960e4a017ccc16894bdae6dce34fb09d7f21ec8cfde88ccbed89c26c6612adf16dba825a02b4477ef618e83091efaa4b59f2d81f16902062ee29bb169e4f23b74d0eb2e9a80f90211a07e045193beaa121e9bd4f7a1aa88ef723722be6b01a7905eabb29bf7954f9f90a025a7579522e9ef773d9089a7e89c7ab15b512119e33bbe68b84e8cd1d33f92b0a0c80d5f5eead097a22f5669a6a09b1b8dd4e77809879ba82bc10c2912dfba9928a0fad6f0c762b324940a2ed88daf34c986a5a08f402e17c700dd23ddccb3b09805a05716ed3cd3a97f060e4e6889de2de9dabb4c48e381855b200ff87a6abd743a52a018e3254b08479a594865115e5bc72b5e74dd4d9e46ca583d9d4bf1d06e7064bba0828fe97a9d75b1b50551eadd5a5b9c20955f81aadb0926ad18512931b6aa8e6ba0d0085e7ebd36c7be94d5dc2ddc8968627b302329af538cd638c8750103b69817a05f93c6c39ae1cc916e9165bda3a4c420aff78652f32b24b07cea821a4ad24327a0034a0eaec5d7b986f8f56c558aaed1a1b8ff1136503dfdd7985addc748428057a08a358e2a3d771f17aad093f61e7bb8305872dd5092ceb615e610c9dd330b693ca0d3bc581e4e124a4bb64b6314f5bdec64faebaf48477508de739d2e3e561cf2a0a06158da0e62a6f34335ac2294bc09d95870ed7ff6827dc96ba24491c282f98bfca023ca1a69e2132545ad89d1a412d2afce25f3ca8d09062109bb03bae117ebdfd8a01e808d97e57f82fe8ca3ef7766a5b49a47635b6930732d68d52477c48b5d1b9ea0b623494d96c239befae49cea940d8000c73bf8140f94d8f9c31afdb4b8fdaf1180f90211a03e7c2180f3cd6d4a75b90d8430029b6e80cee6c94075fc21783e8b72ad199a18a0b47d1c7809fa4d309ddc450c0df23311ad395d8d45a0cd01a84caa68dbbdd503a0d5c6edfddcaaa0a96b24bee6a39149c5ff1fc5c27ac1c97176c2bca3ed9c2880a038aaf16da01eaa865dd28d5714f89ff2fbdf32bc1174c28cbdd1734543d4488aa0ae61e63288db71244b4e76642dd7dfddbbbcd543f7afc6658bbd6cc18ff3a0aaa0c123bfef78683e542eff06e0693e896d945963b0d025c10c311665c478a9a7baa06a96b9244d18763826b2606b84c8b441a531c1a47ce00b285f253a9780d992afa017ac4add3466d235be7cb10da0ffee5d3b02da28517d97bcfcbb252d9b01dde3a04cef6b08eaf66300f0acd6c6a2c65fb5f01aa564f333fdcb3200944f7ffd33bea055faf22be41a521b89dcdd25244d91561f99a1619bc26029adcefdcf37eb5a27a0929ed73c787cf96100b5763d6271986e291a1644868f76dd7d2c0a1362aa6550a090db87ceeb862c49db931ff2eef3f9f5dd0c39eeff6f59ab7dac0695bf084cd3a0ae7bccf15479e634d780683390efb161c96740ff8daf011f3688d2aac33d2cfea03bf17d379a6df590c938c2e69b1ae5a713c7e34fdf1825620b309896f3df676ea0cb970b5f5f5ba1e527bfe82689e2203cb07ddcdc7b0d56538bf296d7ed9eb544a059854c3511ecdca1e5727a40679bbc88a9d453776d155dd5e658707aca3639e580f90211a011be8b5fb88ff7aa28c09cfafcba5a9266a8c6ab7415fec23be9b05e25914549a0090152d2cf7d3ea1cc4ffc10e726be551582387d2705f7c0a6b060ed445d9395a097966335815eecc392d96201c3736c2be7b5c77bd5b800a0c5e19d7703cba974a0a946285bc5898dfb4f83f664accf62864a4e6de047793516b5c6a35f2d38ed43a0e87827afee8ac50223c416f6090f3cfa6c096ad6ecef4be68b776039c6b9e5eba003feda244ae7754eed3f49f073a4b6002d3a00be33137083bce980f691d37ecaa074bf7672ca48de112c4bee7d5246702b6861d21d6e83e5ea38e147fd192bb5c0a0e312120c11fcca90e1f28b26494edb9221523028009bb0f287eff7ed30f98ba3a0bcf3481d30b726e2596b54f0c897000e09e1eecdf3dd337a43f329b4156fd23ca0ef85927f73fb6ea534102b0b565b80c4dd9554232268e56f4ef37597578d456ba09774de1ca83837b2d5cdf15f0b4ef5c4be94f1d544c6061e8f88338f4a42b704a0b9da09c38a401041ce317cabfc29ac87c4a13ea4864b0dc6381c39ff991474a1a0d0e75d69f905de8490006eb3ce0fafb1fa2b1362d0c3937fa76f6c8ca8f843aca07e3f69b7acf34125a0152a2b784eb31fe693013c56f64af2bafda107d8377e95a056b76fc9b3ef6d9239a68e38dadebdf53a187605d4a52978ce8ed5c6d9318d87a0b76756a9cd39fba364a57431ab676c93d732188c865f5a630e0cd49b70d12ea180f90211a0165b4d3bd40cffa63274318510d3f066412b83081630aed6c7994c7697b2f809a04c14d35668a1b86c9931d6d15a8967d960faf5ae6b99ad869a981f512035b205a027590984c4ef7c869efd1102e84a359da86182e751351435233b9b2c450e558ca07b4d3e5387914a8b96722b44259126cb9179b119f0898af5bc9edbc6e11083aaa0dc65fdbd0b217c892ef11fcaf0aa8fd425866cc48558231a30c5a8ddedd04e2ea02e33b12d13b94415c7456211b84fbbfcd2fbf96b35dfbd897e5458f63f597871a0b3a1f07aa206966bb128d308aac69e9c04d8079189e923687e00b09572457ae7a073813e0b0e1e057f716fa315d4657b5f41fbde0016e32a28cfe30eb16e21a8eea08497fe87cabf32c658275ba1621710163ef3a4520e10510043f27f3f082d9f8aa068e03504317fb94e37538a82a0408ed1ea3c1160b22b815bdfc62f091cb7497da0a422a857fca584893c3844d44ea4376400f74ccf4d9ffb32fc063274ba807769a0af490d10258a0f07b1005f363d3b1d91466c49fc4b25a0aabd8b47c9d1caa925a0ca214358f3d132b18ca4cffa730f80b74fc96b0826d12ff4f5fee170226e9568a0f1bbc518f71f588105abb80843439f9e8a947664939395d46e6e31df29c58d7fa05843dd8e31cae42aed665b567d004e9898d525a5938ce3bb8ffc8b94b600004ca00958013dac4df62af26c61fec70b6c2b000fb6e121a3c5156664865b30dd46ac80f901f1a08f4eb7b5d821b9b24551e41128d8a4b3de653abd8a8d80741d32fc5d0cd57d93a00c5060efad572388ce9afaf91488e090d0e7265f5b2a819bc4f45f4491363ee9a0c49ea321de5311eb4467ea7401149b298c861535c3689cef40d504bea6c93aaea00f6c0408af7cb6fe4ee3449fae29331cabff8cc7f9c7ffd1a875e25ef03bcb41a0c96efbd3963092ad575535fff6174a3107e14ecae1fbae49f02300deca62d218a07b63248c4f059ac7e64505f79569cd7a4b86f44a62356285fa272d844b62dd8ca028bfdd748f96b003410fb20d35e48538bb10363d1c0c41d7b8384fb3215b9489a0b76bd898a726d05d0b1f4c994876eab9f91d54a8f386ed88d9b64e1549309e9ca0e12a9c1ff8f987cf534fab733e14915eb119016f094bcf9d02fec3bd323a68cfa0669ec1a83c35d5d3f2ac1ae62bd973afb2881c32db0760bdb243a703885ebf07a080aa95e8dffb9a24f5c1681d7e0cad7b3fde41cf9c2b9a3ed6055024531477f6a07f55683c3947db1f7b825e2b0d6ee1476da95370c879b6405cd5193a0efcb30aa02360e93621045f22c2dd90218af1a0790eed0cd26bc816e858eb0c35f087b7f580a045053947b439f62f2b16f41e83eb4c1873b9be7ce5362acf122a1535b8d5a103a06ee606f1e9703b8d864f712cce8d37179a8e798637903e31806554f72d55475480f85180808080808080a05e95c78f78ec590c001737ada0b4a710ca4ad4039c6e128a81073f176fb4a3e9a0ead00c8f78dcf1931065ec87f9c8f29ec3044bccf0e94f2474916cddf040bb948080808080808080f8669d3c95b4f82d864d940e697d372de64b7397550b1654737dc867833cfde2b846f8440180a087f48fbdefc1df71433106c8d8839989adf1c619c9546780891eabbac3c92af4a0093d9d09c70d7e96055070ed693b893307aa38ee0421e31ccaef4398cd25c150',
            amount_proof_rlp:
                '0xf8d6f8b18080a049fbc0cfd59d5134b4866623fb6452232b73866cc174471272924657d54c57ff8080a0afc054367ea8d102e64acfc11cabd5c627968d856ee2a092aa1100880181c8b78080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a087e2fb4619bfe78f82e422f348334ca76d290f828c5d459612beb6c61caa4e0da01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c380808080e2a030497882cf9008f7f796a89e5514a7b55bd96eab88ecb66aee4fb0a6fd34811c0a',
            block_number: 8287100,
            destination_proof_rlp:
                '0xf8f8f8b18080a049fbc0cfd59d5134b4866623fb6452232b73866cc174471272924657d54c57ff8080a0afc054367ea8d102e64acfc11cabd5c627968d856ee2a092aa1100880181c8b78080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a087e2fb4619bfe78f82e422f348334ca76d290f828c5d459612beb6c61caa4e0da01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c380808080f843a03ab3c568e6b9e23c87101e15642000038e2a634c0eba9355f868407d119483c2a1a0050a0000001600008a8584be3718453e78923713a6966202b05f99c600000038',
        });
    });
});

const mock_RPC_method = (req: any, overrides: Override[]) => {
    for (const override of overrides) {
        if (req.body.method == override.method) {
            return {
                jsonrpc: req.body.jsonrpc,
                id: req.body.id,
                ...override.responses.pop(),
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
