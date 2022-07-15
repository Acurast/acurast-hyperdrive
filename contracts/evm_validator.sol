pragma solidity >=0.7.0 <0.9.0;

contract IBCF_Validator {
    mapping(uint => bytes32) root_history;

    function add_merkle_root_for_level(uint level, bytes32 root) public {
        root_history[level] = root;
    }

    function verify_proof(uint block_level, bytes memory owner, bytes memory key, bytes memory value, bytes32[2][] memory proof) public view {
        bytes32 hash = keccak256(abi.encodePacked(owner, key, value)); // starts with state_hash
        for (uint i=0; i<proof.length; i++) {
            if(proof[i][0] == 0x0) {
                hash = keccak256(abi.encodePacked(hash, proof[i][1]));
            } else {
                hash = keccak256(abi.encodePacked(proof[i][0], hash));
            }
        }
        require(root_history[block_level] == hash);
    }
}
