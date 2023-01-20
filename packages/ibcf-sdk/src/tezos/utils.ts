import { packDataBytes, unpackDataBytes } from '@taquito/michel-codec';

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

export function unpack(value: string, type: MichelsonType) {
    const data: any = unpackDataBytes({ bytes: value.startsWith('0x') ? value.slice(2) : value }, { prim: type });
    switch (type) {
        case MichelsonType.nat:
        case MichelsonType.int:
            return data.int;
        case MichelsonType.address:
            return data.string;
    }
}

export function utf8ToHex(text: string) {
    return Array.from(text).reduce((p, c) => p + c.charCodeAt(0).toString(16), '');
}

/**
 * Pack a tezos address.
 * @param b58Address Base58 encoded address
 * @returns Packed tezos address
 */
export function packAddress(b58Address: string) {
    return pack(b58Address, MichelsonType.address);
}

/**
 * Unpack a tezos address.
 * @param bytes Packed tezos address
 * @returns Base58 encoded address
 */
export function unpackAddress(bytes: string) {
    return unpack(bytes, MichelsonType.address);
}
