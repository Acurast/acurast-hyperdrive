#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod proxy {
    use ink::{
        codegen::EmitEvent,
        env::{
            call::{build_call, ExecutionInput},
            hash, DefaultEnvironment,
        },
        prelude::vec::Vec,
        storage::{traits::StorageLayout, Mapping},
        LangError,
    };
    use scale::{Decode, Encode};
    use scale_info::prelude::cmp::Ordering;

    use acurast_validator_ink::validator::{LeafProof, MerkleProof};

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct SetJobEnvironmentProcessor {
        address: AccountId,
        variables: Vec<(Vec<u8>, Vec<u8>)>,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct UserPayloadSetJobEnvironmentAction {
        job_id: u64,
        public_key: Vec<u8>,
        processors: Vec<SetJobEnvironmentProcessor>,
    }

    pub type SetJobEnvironmentAction = UserPayloadSetJobEnvironmentAction;

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct RegisterJobMatch {
        source: AccountId,
        start_delay: u64,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct UserPayloadRegisterJob {
        allowed_sources: Vec<AccountId>,
        allow_only_verified_sources: bool,
        destination: AccountId,
        required_modules: Vec<u16>,
        script: Vec<u8>,
        duration: u128,
        start_time: u128,
        end_time: u128,
        interval: u64,
        max_start_delay: u64,
        memory: u64,
        network_requests: u32,
        storage: u64,
        // Extra,
        slots: u16,
        reward: u128,
        min_reputation: Option<u32>,
        instant_match: Vec<RegisterJobMatch>,
        expected_fulfillment_fee: u128,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct RegisterJobAction {
        job_id: u64,
        allowed_sources: Vec<AccountId>,
        allow_only_verified_sources: bool,
        destination: AccountId,
        required_modules: Vec<u16>,
        script: Vec<u8>,
        duration: u128,
        start_time: u128,
        end_time: u128,
        interval: u64,
        max_start_delay: u64,
        memory: u64,
        network_requests: u32,
        storage: u64,
        // Extra,
        slots: u16,
        reward: u128,
        min_reputation: Option<u32>,
        instant_match: Vec<RegisterJobMatch>,
        expected_fulfillment_fee: u128,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum UserAction {
        RegisterJob(UserPayloadRegisterJob),
        DeregisterJob(Vec<u64>),
        FinalizeJob(Vec<u64>),
        SetJobEnvironment(UserPayloadSetJobEnvironmentAction),
        Noop,
    }

    #[derive(Clone, Eq, PartialEq, Encode)]
    pub struct OutgoingAction {
        id: u64,
        origin: AccountId,
        payload_version: u16,
        payload: Vec<u8>,
    }

    #[derive(Clone, Eq, PartialEq, Encode)]
    pub enum OutgoingActionPayload {
        RegisterJob(RegisterJobAction),
        DeregisterJob(Vec<u64>),
        FinalizeJob(Vec<u64>),
        SetJobEnvironment(SetJobEnvironmentAction),
        Noop,
    }

    #[derive(Clone, Eq, PartialEq, Decode)]
    pub struct IncomingAction {
        id: u64,
        payload_version: u16,
        payload: Vec<u8>,
    }

    impl Ord for IncomingAction {
        fn cmp(&self, other: &Self) -> Ordering {
            if self.id < other.id {
                Ordering::Less
            } else if self.id > other.id {
                Ordering::Greater
            } else {
                Ordering::Equal
            }
        }
    }

    impl PartialOrd for IncomingAction {
        fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
            Some(self.cmp(other))
        }
    }

    #[derive(Clone, Eq, PartialEq, Decode)]
    pub struct AssignProcessorPayload {
        job_id: u64,
        processor: AccountId,
    }

    #[derive(Clone, Eq, PartialEq, Decode)]
    pub struct FinalizeJobPayload {
        job_id: u64,
        unused_reward: u128,
    }

    #[derive(Clone, Eq, PartialEq, Decode)]
    pub enum IncomingActionPayloadV1 {
        AssignJobProcessor(AssignProcessorPayload),
        FinalizeJob(FinalizeJobPayload),
        Noop,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    pub enum StatusKind {
        /// Status after a job got registered.
        Open = 0,
        /// Status after a valid match for a job got submitted.
        Matched = 1,
        /// Status after all processors have acknowledged the job.
        Assigned = 2,
        /// Status when a job has been finalized or cancelled
        FinalizedOrCancelled = 3,
    }

    pub enum Version {
        V1 = 1,
    }

    #[derive(Clone, Eq, PartialEq, Encode, Decode)]
    pub struct JobInformationV1 {
        creator: AccountId,
        destination: AccountId,
        processors: Vec<AccountId>,
        expected_fulfillment_fee: u128,
        remaining_fee: u128,
        maximum_reward: u128,
        slots: u16,
        status: StatusKind,
        start_time: u128,
        end_time: u128,
        interval: u64,
        abstract_data: Vec<u8>, // Abstract data, this field can be used to add new parameters to the job information structure after the contract has been deployed.
    }

    #[derive(Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum ConfigureArgument {
        SetOwner(AccountId),
        SetMerkleAggregator(AccountId),
        SetProofValidator(AccountId),
        SetPaused(bool),
        SetPayloadVersion(u16),
        SetJobInfoVersion(u16),
        SetMaxMessageBytes(u16),
        SetExchangeRatio(ExchangeRatio),
        SetCode([u8; 32]),
    }

    #[ink(event)]
    pub struct IncomingActionProcessed {
        action_id: u64,
    }

    #[derive(Debug, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo, StorageLayout))]
    pub struct ExchangeRatio {
        pub numerator: u16,
        pub denominator: u16,
    }

    impl ExchangeRatio {
        fn exchange_price(&self, expected_acurast_amount: u128) -> u128 {
            // Calculate how many azero is required to cover for the job cost
            let amount =
                ((self.numerator as u128) * expected_acurast_amount) / (self.denominator as u128);

            if ((self.numerator as u128) * expected_acurast_amount) / (self.denominator as u128)
                != 0
            {
                amount + 1
            } else {
                amount
            }
        }
    }

    /// Contract configurations are contained in this structure
    #[ink::storage_item]
    #[derive(Debug)]
    pub struct Config {
        /// Address allowed to manage the contract
        owner: AccountId,
        /// The state aggregator
        merkle_aggregator: AccountId,
        /// The Merkle Mountain Range proof validator
        proof_validator: AccountId,
        /// Flag that states if the contract is paused or not
        paused: bool,
        /// Payload versioning
        payload_version: u16,
        /// Job information versioning
        job_info_version: u16,
        /// Maximum size per action
        max_message_bytes: u16,
        /// Exchange ratio ( AZERO / ACU )
        exchange_ratio: ExchangeRatio,
    }

    #[ink(storage)]
    pub struct Proxy {
        config: Config,
        next_outgoing_action_id: u64,
        processed_incoming_actions: Mapping<u64, ()>,
        next_job_id: u64,
        actions: Mapping<u64, Vec<u8>>,
        job_info: Mapping<u64, (u16, Vec<u8>)>,
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
            Self {
                config: Config {
                    owner: AccountId::from([0x0; 32]),
                    merkle_aggregator: AccountId::from([0x0; 32]),
                    proof_validator: AccountId::from([0x0; 32]),
                    paused: false,
                    payload_version: 1,
                    job_info_version: 1,
                    max_message_bytes: 2048,
                    exchange_ratio: ExchangeRatio {
                        numerator: 1,
                        denominator: 10,
                    },
                },
                next_outgoing_action_id: 1,
                processed_incoming_actions: Mapping::new(),
                next_job_id: 1,
                actions: Mapping::new(),
                job_info: Mapping::new(),
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
                    ConfigureArgument::SetMerkleAggregator(address) => {
                        self.config.merkle_aggregator = address
                    }
                    ConfigureArgument::SetProofValidator(address) => {
                        self.config.proof_validator = address
                    }
                    ConfigureArgument::SetPaused(paused) => self.config.paused = paused,
                    ConfigureArgument::SetPayloadVersion(version) => {
                        self.config.payload_version = version
                    }
                    ConfigureArgument::SetJobInfoVersion(version) => {
                        self.config.job_info_version = version
                    }
                    ConfigureArgument::SetMaxMessageBytes(max_size) => {
                        self.config.max_message_bytes = max_size
                    }

                    ConfigureArgument::SetExchangeRatio(ratio) => {
                        self.config.exchange_ratio = ratio
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
                    UserAction::RegisterJob(payload) => {
                        // Increment job identifier
                        let job_id = self.next_job_id;
                        self.next_job_id += 1;

                        // Calculate the number of executions that fit the job schedule
                        let start_time = payload.start_time;
                        let end_time = payload.end_time;
                        let interval = payload.interval;
                        assert!(interval > 0, "INTERVAL_CANNNOT_BE_ZERO");
                        let execution_count = (end_time - start_time) / interval as u128;

                        // Calculate the fee required for all job executions
                        let slots = payload.slots;
                        let expected_fulfillment_fee = payload.expected_fulfillment_fee;
                        let expected_fee =
                            ((slots as u128) * execution_count) * expected_fulfillment_fee;

                        // Calculate the total reward required to pay all executions
                        let reward_per_execution = payload.reward;
                        let maximum_reward =
                            (slots as u128) * (execution_count as u128) * reward_per_execution;

                        // Get exchange price
                        let cost: u128 = self.config.exchange_ratio.exchange_price(maximum_reward);

                        // Validate job registration payment
                        assert!(
                            self.env().transferred_value() == expected_fee + cost,
                            "INVALID_FEE_AMOUNT"
                        );

                        let info = JobInformationV1 {
                            creator: self.env().caller(),
                            destination: payload.destination,
                            processors: Vec::new(),
                            expected_fulfillment_fee,
                            remaining_fee: expected_fee,
                            maximum_reward,
                            slots,
                            status: StatusKind::Open,
                            start_time,
                            end_time,
                            interval,
                            abstract_data: Vec::new(),
                        };

                        self.job_info
                            .insert(self.next_job_id, &(Version::V1 as u16, info.encode()));

                        OutgoingActionPayload::RegisterJob(RegisterJobAction {
                            job_id,
                            allowed_sources: payload.allowed_sources,
                            allow_only_verified_sources: payload.allow_only_verified_sources,
                            destination: payload.destination,
                            required_modules: payload.required_modules,
                            script: payload.script,
                            duration: payload.duration,
                            start_time: payload.start_time,
                            end_time: payload.end_time,
                            interval: payload.interval,
                            max_start_delay: payload.max_start_delay,
                            memory: payload.memory,
                            network_requests: payload.network_requests,
                            storage: payload.storage,
                            // Extra
                            slots: payload.slots,
                            reward: payload.reward,
                            min_reputation: payload.min_reputation,
                            instant_match: payload.instant_match,
                            expected_fulfillment_fee: payload.expected_fulfillment_fee,
                        })
                    }
                    UserAction::DeregisterJob(ids) => {
                        for id in ids.clone() {
                            let (version, job_bytes) = self.job_info.get(id).expect("UNKNOWN_JOB");
                            match version {
                                o if o == Version::V1 as u16 => {
                                    let job = JobInformationV1::decode(&mut job_bytes.as_slice())
                                        .expect("COULD_NOT_DECODE_JOB");

                                    // Only the job creator can deregister the job
                                    assert!(job.creator == self.env().caller(), "NOT_JOB_CREATOR");

                                    // Verify if job can be finalized
                                    let is_open = job.status == StatusKind::Open;
                                    assert!(is_open, "CANNOT_CANCEL_JOB");
                                }
                                v => panic!("Unknown job information version: {:?}", v),
                            };
                        }

                        OutgoingActionPayload::DeregisterJob(ids)
                    }
                    UserAction::FinalizeJob(ids) => {
                        for id in ids.clone() {
                            let (version, job_bytes) = self.job_info.get(id).expect("UNKNOWN_JOB");
                            match version {
                                o if o == Version::V1 as u16 => {
                                    let job = JobInformationV1::decode(&mut job_bytes.as_slice())
                                        .expect("COULD_NOT_DECODE_JOB");

                                    // Only the job creator can deregister the job
                                    assert!(job.creator == self.env().caller(), "NOT_JOB_CREATOR");

                                    // Verify if job can be finalized
                                    let is_open = job.status == StatusKind::Open;
                                    let is_expired =
                                        (job.end_time / 1000) < self.env().block_timestamp().into();
                                    assert!(is_open | is_expired, "CANNOT_CANCEL_JOB");
                                }
                                v => panic!("Unknown job information version: {:?}", v),
                            };
                        }

                        OutgoingActionPayload::FinalizeJob(ids)
                    }
                    UserAction::SetJobEnvironment(payload) => {
                        let (version, job_bytes) =
                            self.job_info.get(payload.job_id).expect("UNKNOWN_JOB");
                        match version {
                            o if o == Version::V1 as u16 => {
                                let job = JobInformationV1::decode(&mut job_bytes.as_slice())
                                    .expect("COULD_NOT_DECODE_JOB");

                                // Only the job creator can deregister the job
                                assert!(job.creator == self.env().caller(), "NOT_JOB_CREATOR");
                            }
                            v => panic!("Unknown job information version: {:?}", v),
                        };

                        OutgoingActionPayload::SetJobEnvironment(payload)
                    }
                    UserAction::Noop => OutgoingActionPayload::Noop,
                };

                let encoded_action = OutgoingAction {
                    id: self.next_outgoing_action_id,
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

                let call_result: Result<(), ink::LangError> = build_call::<DefaultEnvironment>()
                    .call(self.config.merkle_aggregator)
                    .exec_input(
                        ExecutionInput::new(acurast_state_ink::INSERT_SELECTOR)
                            .push_arg(Self::blake2b_hash(&encoded_action)),
                    )
                    .transferred_value(0)
                    .returns::<Result<_, LangError>>()
                    .invoke();

                match call_result {
                    // An error emitted by the smart contracting language.
                    // For more details see ink::LangError.
                    Err(lang_error) => {
                        panic!("Unexpected ink::LangError: {:?}", lang_error)
                    }
                    Ok(_) => {
                        // Store encoded action
                        self.actions
                            .insert(self.next_outgoing_action_id, &encoded_action);

                        // Increment action id
                        self.next_outgoing_action_id += 1;
                    }
                }
            }
        }

        #[ink(message)]
        pub fn generate_proof(&self, from: u64, to: u64) -> MerkleProof<[u8; 32]> {
            // Bound checks
            assert!(from > 0, "`from` should be higher than 0");
            assert!(
                to < self.next_outgoing_action_id,
                "`to` should be less then `next_action_id`"
            );

            // normalize leaf position: leafs start on position 0, but actions id's start from 1
            let from_id = from - 1;

            let leaf_index: Vec<u64> = (from_id..=to).collect();
            // Generate proof
            let call_result: Result<
                acurast_state_ink::state_aggregator::MerkleProof<[u8; 32]>,
                ink::LangError,
            > = build_call::<DefaultEnvironment>()
                .call(self.config.merkle_aggregator)
                .exec_input(
                    ExecutionInput::new(acurast_state_ink::GENERATE_PROOF_SELECTOR)
                        .push_arg(leaf_index.clone()),
                )
                .transferred_value(0)
                .returns::<Result<_, LangError>>()
                .invoke();

            match call_result {
                // An error emitted by the smart contracting language.
                // For more details see ink::LangError.
                Err(lang_error) => {
                    panic!("Unexpected ink::LangError: {:?}", lang_error)
                }
                Ok(proof) => {
                    // Prepare result
                    MerkleProof {
                        mmr_size: proof.mmr_size,
                        proof: proof.proof,
                        leaves: leaf_index
                            .iter()
                            .map(|index| LeafProof {
                                leaf_index: *index,
                                data: self.actions.get(index).expect("UNKNOWN_ACTION_ID"),
                            })
                            .collect(),
                    }
                }
            }
        }

        /// This method purpose is to receive provable messages from the acurast protocol
        #[ink(message)]
        pub fn receive_actions(&mut self, snapshot: u128, proof: MerkleProof<[u8; 32]>) {
            // The contract should not be paused
            self.fail_if_paused();

            let mut actions: Vec<IncomingAction> = proof
                .leaves
                .iter()
                .map(|leaf| {
                    IncomingAction::decode(&mut leaf.data.as_slice())
                        .expect("COULD_NOT_DECODE_INCOMING_ACTION")
                })
                .collect();

            // Sort actions
            actions.sort();

            // Validate proof
            let call_result: Result<bool, ink::LangError> = build_call::<DefaultEnvironment>()
                .call(self.config.proof_validator)
                .exec_input(
                    ExecutionInput::new(acurast_validator_ink::VERIFY_PROOF_SELECTOR)
                        .push_arg(snapshot)
                        .push_arg(proof),
                )
                .transferred_value(0)
                .returns::<Result<_, LangError>>()
                .invoke();

            match call_result {
                // An error emitted by the smart contracting language.
                // For more details see ink::LangError.
                Err(lang_error) => {
                    panic!("Unexpected ink::LangError: {:?}", lang_error)
                }
                Ok(is_valid) => {
                    assert!(is_valid, "PROOF_INVALID");
                }
            }

            for action in actions {
                // Verify if message was already processed and fail if it was
                assert!(
                    !self.processed_incoming_actions.contains(action.id),
                    "INVALID_INCOMING_ACTION_ID"
                );
                self.processed_incoming_actions.insert(action.id, &());
                // Decode message
                match action.payload_version {
                    o if o == Version::V1 as u16 => {
                        // Process message
                        let decoded_action =
                            IncomingActionPayloadV1::decode(&mut action.payload.as_slice())
                                .expect("COULD_NOT_DECODE_INCOMING_ACTION_V1");
                        match decoded_action {
                            IncomingActionPayloadV1::AssignJobProcessor(payload) => {
                                let (version, job_bytes) =
                                    self.job_info.get(payload.job_id).expect("UNKNOWN_JOB");
                                match version {
                                    o if o == Version::V1 as u16 => {
                                        let mut job =
                                            JobInformationV1::decode(&mut job_bytes.as_slice())
                                                .expect("COULD_NOT_DECODE_JOB");

                                        // Update the processor list for the given job
                                        job.processors.push(payload.processor);

                                        // Send initial fees to the processor (the processor may need a reveal)
                                        let initial_fee = job.expected_fulfillment_fee;
                                        job.remaining_fee = job.remaining_fee - initial_fee;
                                        // Transfer
                                        self.env()
                                            .transfer(payload.processor, initial_fee)
                                            .expect("COULD_NOT_TRANSFER");

                                        if job.processors.len() == (job.slots as usize) {
                                            job.status = StatusKind::Assigned;
                                        }

                                        // Save changes
                                        self.job_info.insert(payload.job_id, &(o, job.encode()));
                                    }
                                    v => panic!("Unknown job information version: {:?}", v),
                                };
                            }
                            IncomingActionPayloadV1::FinalizeJob(payload) => {
                                let (version, job_bytes) =
                                    self.job_info.get(payload.job_id).expect("UNKNOWN_JOB");
                                match version {
                                    o if o == Version::V1 as u16 => {
                                        let mut job =
                                            JobInformationV1::decode(&mut job_bytes.as_slice())
                                                .expect("COULD_NOT_DECODE_JOB");

                                        // Update job status
                                        job.status = StatusKind::FinalizedOrCancelled;

                                        assert!(
                                            payload.unused_reward <= job.maximum_reward,
                                            "ABOVE_MAXIMUM_REWARD"
                                        );

                                        let refund = job.remaining_fee + payload.unused_reward;
                                        if refund > 0 {
                                            self.env()
                                                .transfer(job.creator, refund)
                                                .expect("COULD_NOT_TRANSFER");
                                        }

                                        // Save changes
                                        self.job_info.insert(payload.job_id, &(o, job.encode()));
                                    }
                                    v => panic!("Unknown job information version: {:?}", v),
                                };
                            }
                            IncomingActionPayloadV1::Noop => {
                                // Intentionally do nothing
                            }
                        }
                    }
                    v => panic!("Unknown incodming action version: {:?}", v),
                }

                // Emit event informing that a given incoming message has been processed
                EmitEvent::<Self>::emit_event(
                    self.env(),
                    IncomingActionProcessed {
                        action_id: action.id,
                    },
                );
            }
        }

        #[ink(message)]
        pub fn fulfill(&mut self, job_id: u64, payload: Vec<u8>) {
            self.fail_if_paused();

            // Get job information
            let (version, job_bytes) = self.job_info.get(job_id).expect("UNKNOWN_JOB");
            match version {
                o if o == Version::V1 as u16 => {
                    let mut job = JobInformationV1::decode(&mut job_bytes.as_slice())
                        .expect("COULD_NOT_DECODE_JOB");

                    // Verify if sender is assigned to the job
                    assert!(
                        job.processors.contains(&self.env().caller()),
                        "NOT_JOB_PROCESSOR",
                    );

                    // Verify that the job has not been finalized
                    assert!(job.status == StatusKind::Assigned, "JOB_ALREADY_FINISHED");

                    // Re-fill processor fees
                    // Forbidden to credit 0ꜩ to a contract without code.
                    let has_funds = job.remaining_fee >= job.expected_fulfillment_fee;
                    let next_execution_fee = if has_funds && job.expected_fulfillment_fee > 0 {
                        job.remaining_fee -= job.expected_fulfillment_fee;

                        job.expected_fulfillment_fee
                    } else {
                        0
                    };

                    // Pass the fulfillment to the destination contract
                    let call_result: Result<(), ink::LangError> =
                        build_call::<DefaultEnvironment>()
                            .call(job.destination)
                            .exec_input(
                                ExecutionInput::new(acurast_consumer_ink::FULFILL_SELECTOR)
                                    .push_arg(job_id)
                                    .push_arg(payload),
                            )
                            .transferred_value(next_execution_fee)
                            .returns::<Result<_, LangError>>()
                            .invoke();

                    match call_result {
                        // An error emitted by the smart contracting language.
                        // For more details see ink::LangError.
                        Err(lang_error) => {
                            panic!("Unexpected ink::LangError: {:?}", lang_error)
                        }
                        Ok(_) => {
                            // Save changes
                            self.job_info.insert(job_id, &(o, job.encode()));
                        }
                    }
                }
                _ => panic!("UNKNOWN_JOB_INFORMATION_VERSION"),
            }
        }
    }
}
