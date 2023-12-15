#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod proxy {
    use ink::prelude::vec;
    use ink::prelude::vec::Vec;
    use ink::storage::Mapping;
    use scale::{Decode, Encode, EncodeLike};
    use ink::env::hash;
    use ink::storage::traits::Packed;

    use acurast_state_ink::state_aggregator::StateAggregatorRef;
    use acurast_validator_ink::validator::ValidatorRef;

    use strum_macros::{EnumString, IntoStaticStr};

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum UserAction {
        RegisterJob {},
        DeregisterJob {},
        FinalizeJob {},
        SetJobEnvironment {},
        Noop,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    pub struct OutgoingAction {
        id: u64,
        origin: AccountId,
        payload_version: u16,
        payload: Vec<u8>,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    pub enum OutgoingActionPayload {
        RegisterJob {},
        DeregisterJob {},
        FinalizeJob {},
        SetJobEnvironment {},
        Noop,
    }

    #[derive(Clone, Eq, PartialEq, EnumString, IntoStaticStr)]
    pub enum IncomingAction {
        #[strum(serialize = "ASSIGN_JOB_PROCESSOR")]
        AssignJobProcessor,
        #[strum(serialize = "FINALIZE_JOB")]
        FinalizeJob,
        #[strum(serialize = "NOOP")]
        Noop = 255,
    }

    /// Convert an index to a IncomingAction
    impl TryFrom<u16> for IncomingAction {
        type Error = Vec<u8>;

        fn try_from(value: u16) -> Result<Self, Self::Error> {
            match value {
                o if o == IncomingAction::AssignJobProcessor as u16 => {
                    Ok(IncomingAction::AssignJobProcessor)
                }
                o if o == IncomingAction::FinalizeJob as u16 => Ok(IncomingAction::FinalizeJob),
                o if o == IncomingAction::Noop as u16 => Ok(IncomingAction::Noop),
                _ => Err(b"Unknown action index".to_vec()),
            }
        }
    }

    #[derive(Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum ConfigureArgument {
        SetOwner(AccountId),
        SetMerkleAggregator(Hash),
        SetProofValidator(Hash),
        SetPaused(bool),
        SetPayloadVersion(u16),
        SetMaxMessageBytes(u16),
        SetCode([u8; 32]),
    }

    #[derive(Decode, Encode, Debug)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo)
    )]
    pub struct LeafProof {
        leaf_index: u64,
        data: Vec<u8>,
    }

    #[derive(Decode, Encode, Debug)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo)
    )]
    pub struct MerkleProof<T: Decode + Packed + EncodeLike> {
        mmr_size: u64,
        proof: Vec<T>,
        leaves: Vec<LeafProof>
    }

    /// Contract configurations are contained in this structure
    #[ink::storage_item]
    #[derive(Debug)]
    pub struct Config {
        /// Address allowed to manage the contract
        owner: AccountId,
        /// The state aggregator
        merkle_aggregator: StateAggregatorRef,
        /// The Merkle Mountain Range proof validator
        proof_validator: ValidatorRef,
        /// Flag that states if the contract is paused or not
        paused: bool,
        /// Payload versioning
        payload_version: u16,
        /// Maximum size per action
        max_message_bytes: u16,
    }

    #[ink(storage)]
    pub struct Proxy {
        config: Config,
        next_action_id: u64,
        actions: Mapping<u64, Vec<u8>>,
    }

    impl Proxy {
        #[ink(constructor)]
        pub fn new(owner: AccountId) -> Self {
            let mut contract = Self::default();

            contract.config.owner = owner;
            contract
        }

        #[ink(constructor)]
        pub fn default() -> Self {
            let merkle_aggregator = StateAggregatorRef::new(AccountId::from([0x0; 32]), 5)
                .code_hash(Hash::try_from([0; 32]).expect("COULD_NOT_INSTANCIATE_STATE_AGGREGATOR"))
                .endowment(0)
                .salt_bytes([0xDE, 0xAD, 0xBE, 0xEF])
                .instantiate();
            let proof_validator = ValidatorRef::new(AccountId::from([0x0; 32]), 0, vec![])
                .code_hash(Hash::try_from([0; 32]).expect("COULD_NOT_INSTANCIATE_STATE_AGGREGATOR"))
                .endowment(0)
                .salt_bytes([0xDE, 0xAD, 0xBE, 0xEF])
                .instantiate();
            Self {
                config: Config {
                    owner: AccountId::from([0x0; 32]),
                    merkle_aggregator,
                    proof_validator,
                    paused: false,
                    payload_version: 1,
                    max_message_bytes: 2048,
                },
                next_action_id: 1,
                actions: Mapping::new(),
            }
        }

        fn fail_if_not_owner(&self) {
            assert!(self.config.owner.eq(&self.env().caller()), "NOT_OWNER");
        }

        /// Panic if the contract is paused
        fn fail_if_paused(&self) {
            assert!(!self.config.paused, "CONTRACT_PAUSED");
        }

        fn blake2b_hash(data: &Vec<u8>) -> [u8; 32] {
            let mut output = <hash::Blake2x256 as hash::HashOutput>::Type::default();
            ink::env::hash_bytes::<hash::Blake2x256>(&data, &mut output);

            output
        }

        /// Modifies the code which is used to execute calls to this contract address (`AccountId`).
        pub fn set_code(&mut self, code_hash: [u8; 32]) {
            ink::env::set_code_hash(&code_hash).unwrap_or_else(|err| {
                panic!(
                    "Failed to `set_code_hash` to {:?} due to {:?}",
                    code_hash, err
                )
            });
            ink::env::debug_println!("Switched code hash to {:?}.", code_hash);
        }

        #[ink(message)]
        pub fn configure(&mut self, actions: Vec<ConfigureArgument>) {
            self.fail_if_not_owner();

            for a in actions {
                match a {
                    ConfigureArgument::SetOwner(address) => self.config.owner = address,
                    ConfigureArgument::SetMerkleAggregator(code_hash) => {
                        self.config.merkle_aggregator =
                            StateAggregatorRef::new(AccountId::from([0x0; 32]), 5)
                                .code_hash(code_hash)
                                .endowment(0)
                                .salt_bytes([0xDE, 0xAD, 0xBE, 0xEF])
                                .instantiate()
                    }
                    ConfigureArgument::SetProofValidator(code_hash) => {
                        self.config.proof_validator =
                            ValidatorRef::new(AccountId::from([0x0; 32]), 0, vec![])
                                .code_hash(code_hash)
                                .endowment(0)
                                .salt_bytes([0xDE, 0xAD, 0xBE, 0xEF])
                                .instantiate()
                    }
                    ConfigureArgument::SetPaused(paused) => self.config.paused = paused,
                    ConfigureArgument::SetPayloadVersion(version) => {
                        self.config.payload_version = version
                    }
                    ConfigureArgument::SetMaxMessageBytes(max_size) => {
                        self.config.max_message_bytes = max_size
                    }
                    ConfigureArgument::SetCode(code_hash) => self.set_code(code_hash),
                }
            }
        }

        /// This method is called by users to interact with the acurast protocol
        #[ink(message)]
        pub fn send_actions(&mut self, actions: Vec<UserAction>) {
            // The contract should not be paused
            self.fail_if_paused();

            let caller = self.env().caller();

            for action in actions {
                let outgoing_action = match action {
                    UserAction::RegisterJob {} => todo!(),
                    UserAction::DeregisterJob {} => todo!(),
                    UserAction::FinalizeJob {} => todo!(),
                    UserAction::SetJobEnvironment {} => todo!(),
                    UserAction::Noop => OutgoingActionPayload::Noop,
                };

                let encoded_action = OutgoingAction {
                    id: self.next_action_id,
                    origin: caller,
                    payload_version: self.config.payload_version,
                    payload: outgoing_action.encode(),
                }
                .encode();

                // Verify that the encoded action size is less than `next_action_id`
                assert!(
                    encoded_action
                        .len()
                        .lt(&(self.config.max_message_bytes as usize)),
                    "ACTION_TOO_BIG"
                );

                // Store encoded action
                self.actions.insert(self.next_action_id, &encoded_action);

                // Increment action id
                self.next_action_id += 1;

                self.config.merkle_aggregator.insert(Self::blake2b_hash(&encoded_action))
            }
        }

        #[ink(message)]
        pub fn generate_proof(&self, from: u64, to: u64) -> MerkleProof<[u8; 32]> {
            // Bound checks
            assert!(from > 0, "`from` should be higher than 0");
            assert!(to < self.next_action_id, "`to` should be less then `next_action_id`");

            // normalize leaf position: leafs start on position 0, but actions id's start from 1
            let from_id = from - 1;

            let leaf_index: Vec<u64> = (from_id..=to).collect();
            // Generate proof
            let proof = self.config.merkle_aggregator.generate_proof(leaf_index.clone());

            // Prepare result
            MerkleProof {
                mmr_size: proof.mmr_size,
                proof: proof.proof,
                leaves: leaf_index.iter().map(|index| {
                    LeafProof {
                        leaf_index: *index,
                        data: self.actions.get(index).expect("UNKNOWN_ACTION_ID")
                    }
                }).collect()
            }
        }

        /// This method purpose is to receive provable messages from the acurast protocol
        #[ink(message)]
        pub fn receive_actions(&mut self) {
            // The contract should not be paused
            self.fail_if_paused();

            // Validate proof

            // Decode message
            let action = 1;

            // Process message
            match IncomingAction::try_from(action).expect("Unknown action") {
                IncomingAction::AssignJobProcessor => todo!(),
                IncomingAction::FinalizeJob => todo!(),
                IncomingAction::Noop => {
                    // Intentionally do nothing
                }
            }
        }
    }
}
