const Web3 = require("web3");
const { Trie } = require("@ethereumjs/trie");
const RLP = require("rlp");

const trie = new Trie();
const web3_sdk = new Web3(
  "https://goerli.infura.io/v3/d100ca58b1cc4ea98873b4f0ddd7894c"
);

const ETH_BRIDGE_ADDRESS =
  process.argv[2] || "0xF8D0dcb8F3Af348586360971b3561B3b139a2929";

const ACCOUNT_STATE_ROOT_INDEX = 2;

const ETH_BLOCK_NUMBER = 8287500;
const destinationRegistryIndex = "05".padStart(64, "0");
const amountRegistryIndex = "06".padStart(64, "0");
const hexNonce = Web3.utils.toHex(1).slice(2).padStart(64, "0");
const destinationSlot = Web3.utils.sha3(
  "0x" + hexNonce + destinationRegistryIndex
);
const amountSlot = Web3.utils.sha3("0x" + hexNonce + amountRegistryIndex);

(async () => {
  const [block, account] = await Promise.all([
    web3_sdk.eth.getBlock(ETH_BLOCK_NUMBER),
    web3_sdk.eth.getProof(
      ETH_BRIDGE_ADDRESS,
      [destinationSlot, amountSlot],
      ETH_BLOCK_NUMBER
    ),
  ]);
  console.log([destinationSlot, amountSlot]);
  const blockStateRoot = Buffer.from(block.stateRoot.slice(2), "hex");
  const acountkey = Buffer.from(
    Web3.utils.sha3(ETH_BRIDGE_ADDRESS).slice(2),
    "hex"
  );
  const accountProof = account.accountProof.map((x) =>
    Buffer.from(x.slice(2), "hex")
  );
  const destinationProof = account.storageProof[0].proof.map((x) =>
    Buffer.from(x.slice(2), "hex")
  );
  const amountProof = account.storageProof[1].proof.map((x) =>
    Buffer.from(x.slice(2), "hex")
  );

  const account_proof_rlp = Buffer.from(
    RLP.encode(account.accountProof.map((r) => RLP.decode(r)))
  ).toString("hex");
  const destination_proof_rlp = Buffer.from(
    RLP.encode(account.storageProof[0].proof.map((r) => RLP.decode(r)))
  ).toString("hex");
  const amount_proof_rlp = Buffer.from(
    RLP.encode(account.storageProof[1].proof.map((r) => RLP.decode(r)))
  ).toString("hex");

  console.log({
    ETH_ACCOUNT_PROOF: account_proof_rlp,
    ETH_DESTINATION_PROOF: destination_proof_rlp,
    ETH_AMOUNT_PROOF: amount_proof_rlp,
    ETH_BRIDGE_ADDRESS,
    ETH_BLOCK_NUMBER,
    ETH_BLOCK_ROOT_STATE: block.stateRoot,
  });

  try {
    const value = await trie.verifyProof(
      blockStateRoot,
      acountkey,
      accountProof
    );

    // Validate account
    if (
      !value ||
      !value.equals(
        Buffer.from(
          RLP.encode([
            Number(account.nonce),
            Number(account.balance),
            account.storageHash,
            account.codeHash,
          ])
        )
      )
    )
      console.log("proof failed");
    else console.log("Account proof is valid!");
    console.log(account.storageProof);
    const accountStateRoot = RLP.decode(value)[ACCOUNT_STATE_ROOT_INDEX];
    const destination = await trie.verifyProof(
      accountStateRoot,
      Buffer.from(Web3.utils.sha3(destinationSlot).slice(2), "hex"),
      destinationProof
    );
    console.log("Destination:", destination);
    const amount = await trie.verifyProof(
      accountStateRoot,
      Buffer.from(Web3.utils.sha3(amountSlot).slice(2), "hex"),
      amountProof
    );
    console.log("Amount:", amount);
  } catch (e) {
    console.log(e);
  }
})();
