#import "../../../../contracts/tezos/ligo/libs/bytes.mligo" "Utils_bytes"

let test_bytes_of_nat =
    let result = Test.run Utils_bytes.of_nat 32592575621351777380295131014550050576823494298654980010178247189670100796213387298934358015n in
    let expected_result = Test.eval (0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff) in
    let () = assert (Test.michelson_equal result expected_result) in
    let result = Test.run Utils_bytes.of_nat 280n in
    let expected_result = Test.eval (0x0118) in
    assert (Test.michelson_equal result expected_result)

let test_pad_start =
    let result = Test.run Utils_bytes.pad_start (0xff, 0x00, 10n) in
    let expected_result = Test.eval (0x000000000000000000ff) in
    assert (Test.michelson_equal result expected_result)
