import { hexOfUint8Array } from '../src/misc';

describe('Miscellaneous', () => {
    it('hexOfUint8Array', () => {
        expect(hexOfUint8Array(Uint8Array.of(0, 1, 2, 3, 4, 255))).toBe('0001020304ff');
    });
});
