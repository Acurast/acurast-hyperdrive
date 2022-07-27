import { packDataBytes } from '@taquito/michel-codec';

export const pack_nat = (nat: number): string => packDataBytes({ int: String(nat) }, { prim: 'nat' }).bytes;
export const pack_address = (address: string): string =>
    '0x' + packDataBytes({ string: address }, { prim: 'address' }).bytes;
