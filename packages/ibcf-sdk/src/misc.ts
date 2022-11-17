/**
 * Encode Uint8Array to a hexadecimal string.
 * @param arr A stream of bytes.
 * @returns Hexadecimal string.
 */
export function hexOfUint8Array(arr: Uint8Array) {
    return arr.reduce((hex, byte) => hex + byte.toString(16).padStart(2, '0'), '');
}
