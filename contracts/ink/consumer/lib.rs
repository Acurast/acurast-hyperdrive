#![cfg_attr(not(feature = "std"), no_std, no_main)]

use ink::env::call::Selector;

pub const FULFILL_SELECTOR: Selector = Selector::new(ink::selector_bytes!("fulfill"));

#[ink::contract]
mod client {
    use ink::{
        prelude::vec::Vec,
    };

    #[ink(storage)]
    pub struct Client {}

    impl Client {
        /// Constructor that initializes the `bool` value to the given `init_value`.
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {}
        }

        #[ink(message)]
        pub fn fulfill(&mut self, job_id: u64, payload: Vec<u8>) {}
    }
}
