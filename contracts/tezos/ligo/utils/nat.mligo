#import "./bytes.mligo" "Bytes_utils"
#import "./math.mligo" "Math"

let of_bytes (b: bytes) =
    let length = Bytes.length b in
    let rec for_range (from, to, result : nat * nat * nat) : nat =
        if from = to
        then
            result
        else
            let byte : bytes = Bytes.sub from 1n b in
            let base : nat = Option.unopt (is_nat (length - (from + 1))) * 2n in
            // - Packed prefix: 0x05 (1 byte)
            // - Data identifier: (bytes = 0x0a) (1 byte)
            // - Length ("0x00000020" = 32) (4 bytes)
            let packed_prefix = 0x050a00000020 in
            // - Data (byte + 31 bytes)
            let packed_bytes : bytes = Bytes_utils.concat [packed_prefix; byte; 0x00000000000000000000000000000000000000000000000000000000000000] in
            let value : int = int (Option.unopt (Bytes.unpack packed_bytes) : bls12_381_fr) in
            let result = result + Option.unopt (is_nat (value * Math.pow(16n, base))) in
            for_range(from+1n, to, result)
    in
    for_range(0n, length, 0n)
