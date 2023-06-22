#include "../../../ligo-smart-contracts/single_asset/ligo/src/fa2_single_asset.mligo"

type storage = {
    admin : simple_admin_storage;
    // A facilitator (e.g., a protocol, an entity, etc.) has the ability to trustlessly generate (and burn) ACRST tokens.
    facilitators: address set;
    assets : single_token_storage;
    metadata : contract_metadata;
}

type update_facilitators_action =
[@layout:comb]
    | Add of address
    | Remove of address

type extended_param =
    | Admin of simple_admin
    | Assets of fa2_entry_points
    | Tokens of token_manager
    | Update_facilitators of update_facilitators_action list
    | Set_metadata of contract_metadata

let fail_if_not_facilitator (facilitators: address set): unit =
    if Set.mem (Tezos.get_sender()) facilitators
    then unit
    else failwith "NOT_A_FACILITATOR"

let main (param, storage : extended_param * storage): (operation list) * storage =
    match param with
    | Admin p ->
        let ops, admin = simple_admin (p, storage.admin) in
        let new_s = { storage with admin = admin; } in
        (ops, new_s)
    | Tokens p ->
        let _ = fail_if_not_facilitator storage.facilitators in

        let ops, assets = token_manager (p, storage.assets) in
        let new_s = { storage with assets = assets; } in
        (ops, new_s)
    | Assets p ->
        let _ = fail_if_paused storage.admin in

        let ops, assets = fa2_main (p, storage.assets) in
        let new_s = { storage with assets = assets; } in
        (ops, new_s)
    | Update_facilitators p ->
        let _ = fail_if_not_admin storage.admin in
        // Update facilitators list
        let update_facilitators(acc, update : address set * update_facilitators_action): address set = match update with
        | Add facilitator -> Set.add facilitator acc
        | Remove facilitator -> Set.remove facilitator acc
        in
        ([], { storage with facilitators = List.fold update_facilitators p storage.facilitators; })
    | Set_metadata p ->
        let _ = fail_if_not_admin storage.admin in

        let new_storage = { storage with metadata = p; } in
        ([], new_storage)
