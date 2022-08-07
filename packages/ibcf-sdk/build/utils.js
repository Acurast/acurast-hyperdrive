import { packDataBytes } from '@taquito/michel-codec';
export var MichelsonType;
(function (MichelsonType) {
    MichelsonType["nat"] = "nat";
    MichelsonType["int"] = "int";
    MichelsonType["address"] = "address";
})(MichelsonType || (MichelsonType = {}));
export function pack(value, type) {
    switch (type) {
        case MichelsonType.nat:
        case MichelsonType.int:
            return packDataBytes({ int: String(value) }, { prim: type }).bytes;
        case MichelsonType.address:
            return packDataBytes({ string: String(value) }, { prim: type }).bytes;
    }
}
export function utf8ToHex(text) {
    return Array.from(text).reduce((p, c) => p + c.charCodeAt(0).toString(16), "");
}
