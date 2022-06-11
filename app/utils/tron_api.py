from tronapi import Tron
from tronapi import HttpProvider
from trx_utils import is_address
from trx_utils import to_hex, encode_hex

import requests
import base58
import base64

from config import Config
net_work = "https://api.trongrid.io"
CONTRACT_ADDRESS = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t" # MAin
# net_work = "https://api.shasta.trongrid.io"
# CONTRACT_ADDRESS = "TYAL3ryvhA9HbJRLzsK7vKjLpkC1ZoQTcR" # Test
full_node = HttpProvider(net_work)
solidity_node = HttpProvider(net_work)
event_server = HttpProvider(net_work)

tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)
tron.private_key = Config().TRON_PRIVATE_KEY
tron.default_address = Config().TRON_DEFAULT_ADDRESS
def transferTrx(_to, value):
    try:
        send = tron.trx.send_transaction(_to, float(value))
        data = {
            "status": True,
            "txid": send['txid']
        }
        return data
    except Exception as e:
        print(e)
        data = {
            "status": False
        }
        return data
def isAddress(address):
    try:
        is_valid = is_address(address)
        print('is_valid', is_valid)
        return is_valid
    except Exception as e:
        print('e',e)
        return False


def send_usdt(to_address: str, amount: float):
    kwargs = dict()
    kwargs["contract_address"] = tron.address.to_hex(CONTRACT_ADDRESS)
    kwargs["function_selector"] = "transfer(address,uint256)"
    kwargs["call_value"] = 0
    kwargs["parameters"] = [
        {
            'type': 'address',
            'value': tron.address.to_hex(to_address)
        },
        {
            'type': 'uint256',
            'value': int(float(amount)*pow(10,6))
        }
    ]
    try:
        raw_tx = tron.transaction_builder.trigger_smart_contract(**kwargs)
        sign = tron.trx.sign(raw_tx["transaction"])
        result = tron.trx.broadcast(sign)
        if 'result' in result and result['result'] is True:
            print("success", result['txid'])
            return result['txid']
        else:
            return False
    except Exception as e:
        print('e',e)
        return False

# send_usdt('TGtNXZi92q3pGyrEgreaQth', 1)
