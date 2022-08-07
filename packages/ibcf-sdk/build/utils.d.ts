export declare enum MichelsonType {
    nat = "nat",
    int = "int",
    address = "address"
}
export declare function pack(value: string | number, type: MichelsonType): string;
export declare function utf8ToHex(text: string): string;
