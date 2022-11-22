import { MichelsonType, pack, packAddress, unpack } from '../../src/tezos/utils';

describe('Tezos > Utils', () => {
    it('pack', () => {
        expect(pack(1, MichelsonType.nat)).toBe('050001');
        expect(pack(9999, MichelsonType.int)).toBe('05008f9c01');
        expect(pack('tz1f2k9M3ztqtbCTk5EmEepboEJxksXvafaU', MichelsonType.address)).toBe(
            '050a000000160000d4b624c3100fd8b0cfb44941d0361dac52a660d5',
        );
    });
    it('unpack', () => {
        expect(unpack('050001', MichelsonType.nat)).toBe('1');
        expect(unpack('05008f9c01', MichelsonType.int)).toBe('9999');
        expect(unpack('050a000000160000d4b624c3100fd8b0cfb44941d0361dac52a660d5', MichelsonType.address)).toBe(
            'tz1f2k9M3ztqtbCTk5EmEepboEJxksXvafaU',
        );
    });
    it('packAddress', () => {
        expect(packAddress('tz1f2k9M3ztqtbCTk5EmEepboEJxksXvafaU')).toBe(
            '050a000000160000d4b624c3100fd8b0cfb44941d0361dac52a660d5',
        );
        expect(packAddress('tz28QJHLyqvaY2rXAoFZTbxrXeD88NA8wscC')).toBe(
            '050a00000016000100f51a32c263f048c731d0c29ee9caddac7410af',
        );
        expect(packAddress('tz3QfPf2v3NM7k1MHMkCZs9Jmnr25xhUSWNN')).toBe(
            '050a0000001600022f8922bd6928f35c6c7e342e8c91963c6e5b8477',
        );
        expect(packAddress('KT1Tezooo3zzSmartPyzzSTATiCzzzseJjWC')).toBe(
            '050a0000001601d1371b91c7491542e97deee96091e28a80b2335900',
        );
    });
});
