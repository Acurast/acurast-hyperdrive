import { packDataBytes } from '@taquito/michel-codec';
import { b58cdecode, prefix } from '@taquito/utils';
import { hexOfUint8Array } from '../misc';

export enum MichelsonType {
    nat = 'nat',
    int = 'int',
    address = 'address',
}

export function pack(value: string | number, type: MichelsonType) {
    switch (type) {
        case MichelsonType.nat:
        case MichelsonType.int:
            return packDataBytes({ int: String(value) }, { prim: type }).bytes;
        case MichelsonType.address:
            return packDataBytes({ string: String(value) }, { prim: type }).bytes;
    }
}

export function utf8ToHex(text: string) {
    return Array.from(text).reduce((p, c) => p + c.charCodeAt(0).toString(16), '');
}

/**
 * Pack a tezos address.
 * @param b58Address Base58 encoded address
 */
export function packAddress(b58Address: string) {
    return pack(b58Address, MichelsonType.address);
}