from web3.auto import w3, Web3
from eth_account.messages import encode_defunct

private_key = str("e8529dd47ef64bf253e46ac47a572abe0e2c87a6ee441eef708dde07ee7a382c")

message = encode_defunct(
    hexstr="0x0000000000000000000000000000000000000000000000000000000000000001836f1abf07dbdb7f262d0a71067dadc421fe3df0"
)

signed_message = w3.eth.account.sign_message(message, private_key=private_key)
print(f"v: {signed_message.v}")
print(f"r: {Web3.toHex(signed_message.r)}")
print(f"s: {Web3.toHex(signed_message.s)}")
