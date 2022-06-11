from web3 import Web3, WebsocketProvider, HTTPProvider

import json
import logging
import time
from threading import Thread
from config import Config
from . import helpers
from datetime import datetime
# w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
# w3.eth.defaultAccount = w3.eth.accounts[0]
providerHttp = None
providerSocket = None
web3_socket= None
infura_url = Config().infura_url
providerHttp = HTTPProvider(infura_url)

web3 = Web3(providerHttp)



infura_url_ws = Config().PROVIDER_WS
# providerSocket = WebsocketProvider(infura_url_ws)
# web3_socket = Web3(providerSocket)

if not web3.isConnected():
    print('ETH node connection error!')
    exit(1)

contractAddress = web3.toChecksumAddress(Config().contractAddress)
c_abi = json.loads('[ { "constant": false, "inputs": [], "name": "acceptOwnership", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "spender", "type": "address" }, { "name": "tokens", "type": "uint256" } ], "name": "approve", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "spender", "type": "address" }, { "name": "tokens", "type": "uint256" }, { "name": "data", "type": "bytes" } ], "name": "approveAndCall", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "to", "type": "address" }, { "name": "tokens", "type": "uint256" } ], "name": "transfer", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "tokenAddress", "type": "address" }, { "name": "tokens", "type": "uint256" } ], "name": "transferAnyERC20Token", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "from", "type": "address" }, { "name": "to", "type": "address" }, { "name": "tokens", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "_newOwner", "type": "address" } ], "name": "transferOwnership", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "payable": true, "stateMutability": "payable", "type": "fallback" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "_from", "type": "address" }, { "indexed": true, "name": "_to", "type": "address" } ], "name": "OwnershipTransferred", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "from", "type": "address" }, { "indexed": true, "name": "to", "type": "address" }, { "indexed": false, "name": "tokens", "type": "uint256" } ], "name": "Transfer", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "tokenOwner", "type": "address" }, { "indexed": true, "name": "spender", "type": "address" }, { "indexed": false, "name": "tokens", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "constant": true, "inputs": [], "name": "_totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "tokenOwner", "type": "address" }, { "name": "spender", "type": "address" } ], "name": "allowance", "outputs": [ { "name": "remaining", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "tokenOwner", "type": "address" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "name": "", "type": "uint8" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "name", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "newOwner", "outputs": [ { "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "owner", "outputs": [ { "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "a", "type": "uint256" }, { "name": "b", "type": "uint256" } ], "name": "safeAdd", "outputs": [ { "name": "c", "type": "uint256" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": true, "inputs": [ { "name": "a", "type": "uint256" }, { "name": "b", "type": "uint256" } ], "name": "safeDiv", "outputs": [ { "name": "c", "type": "uint256" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": true, "inputs": [ { "name": "a", "type": "uint256" }, { "name": "b", "type": "uint256" } ], "name": "safeMul", "outputs": [ { "name": "c", "type": "uint256" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": true, "inputs": [ { "name": "a", "type": "uint256" }, { "name": "b", "type": "uint256" } ], "name": "safeSub", "outputs": [ { "name": "c", "type": "uint256" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" } ]')
contract = web3.eth.contract(address=contractAddress, abi=c_abi)
# Contract_socket = web3_socket.eth.contract(abi=c_abi, address=contractAddress)
chainId = web3.eth.chainId
gasPrice = web3.eth.gasPrice
gas = 700000
def waitForTransaction(txHash, modus):
    web3.eth.waitForTransactionReceipt(txHash)
    print('modus', modus)

def transferToken(_to, value, id):
    private_key = Config().private_key # Fill me in
    from_address = web3.toChecksumAddress(Config().fromAddress)
    to_addresses = web3.toChecksumAddress(_to)
    value = web3.toWei(value, 'ether')
    transaction = contract.functions.transfer(to_addresses, value).buildTransaction({
        'chainId': chainId,
        'gas': gas,
        'nonce': web3.eth.getTransactionCount(from_address, "pending")
    })
    signedTransaction = web3.eth.account.signTransaction(transaction, private_key)
    txHash = web3.eth.sendRawTransaction(signedTransaction.rawTransaction)
    # receipt = web3.eth.waitForTransactionReceipt(txHash)
    # print('dddddddd', receipt)
    # Receipt AttributeDict({'blockHash': HexBytes('0x14a043a93b5045e4fdc5ba57bd9683f623a81c311f350222e8ea6855b4782f00'), 'blockNumber': 7829081, 'contractAddress': None, 'cumulativeGasUsed': 2443586, 'from': '0x7186d373a19f7dd6cA046e13eE9e31d3D4c01f6F', 'gasUsed': 36182, 'logs': [AttributeDict({'address': '0x8Ebf46cde233478Fd392b6D8f02D33Fb9c2bC33d', 'blockHash': HexBytes('0x14a043a93b5045e4fdc5ba57bd9683f623a81c311f350222e8ea6855b4782f00'), 'blockNumber': 7829081, 'data': '0x0000000000000000000000000000000000000000000000026203151c73120000', 'logIndex': 6, 'removed': False, 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x0000000000000000000000007186d373a19f7dd6ca046e13ee9e31d3d4c01f6f'), HexBytes('0x000000000000000000000000899a5888a5c9ea8f359511d401f1f9a7a8c9eb5c')], 'transactionHash': HexBytes('0xb5b03c6ae52d4f2e96f286a9ac25b461c6fa43c22c7e3a43bbb859a02e311fd1'), 'transactionIndex': 42})], 'logsBloom': HexBytes('0x00000000080000000000000000000000200000000000000000100000000000000000000000000000000000000400000000000002000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000010000000000000001000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008'), 'status': 1, 'to': '0x8Ebf46cde233478Fd392b6D8f02D33Fb9c2bC33d', 'transactionHash': HexBytes('0xb5b03c6ae52d4f2e96f286a9ac25b461c6fa43c22c7e3a43bbb859a02e311fd1'), 'transactionIndex': 42})
    
    return txHash.hex()
    # print("TxHash: ", txHash.hex())   
    # worker = Thread(target=waitForTransaction, args=(txHash, "Create"), daemon=True)
    # worker.start()
    # print("workerworkerTxHash: ", txHash.hex()) 

def create_new_wallet_via_web3():
    PASSWORD = 'nole'
    acct = web3.eth.account.create(PASSWORD)
    print('my address is     : {}'.format(acct.address))
    print('my private key is : {}'.format(acct.privateKey.hex()))
    json = web3.eth.account.encrypt(acct.privateKey,PASSWORD)
    data = {
        "address": acct.address,
        "key": acct.privateKey.hex()
    }
    return data


def get_balance(address):
    balance = contract.functions.balanceOf(address).call()
    print(web3.fromWei(balance, 'ether'))
    return web3.fromWei(balance, 'ether')

def filter_loop(mongo):
    event_filter = Contract_socket.events.Transfer.createFilter(fromBlock='latest')
    while True:
        data = event_filter.get_new_entries()
        for event in data:
            print(event['args']) 
            from_address = event['args']['from']
            to_address = event['args']['to']
            amount = web3.fromWei(event['args']['tokens'], 'ether')
            amount_satoshi = float(amount)*100000000
            print(from_address, to_address, amount)
            user = mongo.db.Users.find_one({'wallet.qtc_address' : to_address })
            if user is not None:
                new_balance = float(user['wallet']['coin_balance'])+float(amount_satoshi)
                mongo.db.Users.update({'_id' : user['_id'] },{'$set' : {'wallet.coin_balance' : new_balance}})
                _id = helpers.getNextSequence(mongo.db.Counters,"DepositId")
                transaction_id = 'T%s' % (helpers.generate_transaction_id(_id))
                data_withdraw = {
                    "_id": _id,
                    "transaction_id": transaction_id,
                    'currency': 'QTC',
                    'address': to_address,
                    'amount_coin_satoshi': round(float(amount_satoshi), 0),                
                    'user_id' : user['_id'],
                    "status": 1,
                    "createdAt": datetime.now()
                }
                withdraw_id = mongo.db.Deposits.insert(data_withdraw)
        time.sleep(5)