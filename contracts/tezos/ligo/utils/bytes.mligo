let concat (bs : bytes list) : bytes = [%Michelson ({| { CONCAT } |} : bytes list -> bytes)] bs

let pad_start(b, fill, length: bytes * bytes * nat): bytes =
    let rec pad (prefix, length: bytes * nat): bytes =
        let prefix_length = Bytes.length prefix in
        if prefix_length < length then pad((Bytes.concat fill prefix), length) else prefix
    in
    let diff = Option.unopt (is_nat (length - (Bytes.length b))) in
    let prefix = pad(0x, diff) in
    Bytes.concat prefix b

(* Convert 8-bit nat into bytes *)
let of_nat8(n: nat): bytes =
    let () = assert_with_error (n < 256n) "NUMBER_TOO_BIG" in
    let one: bls12_381_fr = 0x01 in
    let packed = Bytes.pack (int(n) * one) in
    Bytes.sub 6n 1n packed

let of_nat(n: nat): bytes =
    let rec convert(n, byte_seq, left_nibble: nat * bytes list * nat option): bytes =
        if n = 0n
        then
            let byte_seq = match left_nibble with
            | Some (v) ->
                let byte = of_nat8(Bitwise.or (Bitwise.shift_left 0n 4n) v) in
                (byte :: byte_seq)
            | None -> byte_seq
            in
            (concat byte_seq)
        else
            let (quotient, remainder) : (nat * nat) = Option.unopt (ediv n 16n) in
            let left_nibble, byte_seq = match left_nibble with
            | Some (v) ->
                let byte = of_nat8(Bitwise.or (Bitwise.shift_left remainder 4n) v) in
                (None, byte :: byte_seq)
            | None -> (Some(remainder), byte_seq)
            in
            convert(quotient, byte_seq, left_nibble)
    in
    convert(n, [], None)
