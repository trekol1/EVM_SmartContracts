from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")
# Compile my Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("comipiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to rinkeby
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/c4755a2725794bb58a01c2d892c8f6a0")
)
chain_id = 4
my_address = "0xC1bc0195F9eCBF4E085cb847eEc03e9a266a7ED3"
private_key = os.getenv("PRIVATE_KEY")

# Creating a contract on python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction count
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)
# 1.Build transaction
# 2.Sign transaction
# 3.Send transaction
# transaction = SimpleStorage.constructor().buildTransaction(
# {"chainId": chain_id, "from": my_address, "nonce": nonce}
# )

# build txn
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

# sign txn
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send txn
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with a contract you always need:
# 1. Contract address
# 2. Contract ABI
simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
# Call -> Simulate making a call and getting return value
# Transact -> Actually make state change

# Initial value of favorite number
print("Initial value of favorite number:")
print(simple_storage.functions.retrieve().call())
print("Creating transaction to store new favorite number")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("Sending signed transaction")
transaction_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(transaction_hash)
print("New favorite number: ", simple_storage.functions.retrieve().call())
