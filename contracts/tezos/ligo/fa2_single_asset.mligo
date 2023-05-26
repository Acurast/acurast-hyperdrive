#include "../../../ligo-smart-contracts/single_asset/ligo/src/fa2_single_asset.mligo"

type extended_param =
  | Single_asset of single_asset_param
  | Set_metadata of contract_metadata

let main
    (param, s : extended_param * single_asset_storage)
  : (operation list) * single_asset_storage =
  match param with
  | Single_asset p -> single_asset_main (p, s)
  | Set_metadata p ->
    let _ = fail_if_not_admin s.admin in

    let new_storage = { s with metadata = p; } in
    ([], new_storage)
