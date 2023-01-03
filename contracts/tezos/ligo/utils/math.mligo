// Adapted from https://github.com/ligolang/math-lib-cameligo/blob/main/core/math.mligo

let rec fast_power : nat -> nat -> nat -> nat = fun a b result ->
    if b = 0n then result
    else
        let result = if (b land 1n) = 1n then result * a else result in
        let b = b lsr 1n in
        let a = a * a in
        fast_power a b result

(* return x ^ y *)
let pow (x, y : nat * nat) : nat = fast_power x y 1n
