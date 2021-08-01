# Import dependencies
import subprocess
import json
import os

from dotenv import load_dotenv

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from pprint import pprint

#from eth_account import Account
from web3 import Web3, middleware, Account
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --coin={coin} --numderive={depth} --format=json --cols=all'
    #print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    #print(output)
    p_status = p.wait()
    return json.loads(output)

# # Create a dictionary object called coins to store the output from `derive_wallets`.
def coins():
    coin_dict = {
        'btc' : derive_wallets(BTC, mnemonic, 3),
        'eth' : derive_wallets(ETH, mnemonic, 3),
        'btc-test' : derive_wallets(BTCTEST, mnemonic, 3),
    }
    return coin_dict

# # Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# # Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        tx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return tx_data
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    raw_tx = create_tx(coin, account, recipient, amount)
    signed_tx = account.sign_transaction(raw_tx)
    if coin == ETH:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)

# BTCTEST Transaction
coins_value = coins()
#print (coins_value [BTCTEST][0]['privkey'])
#account = priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey'])
btc_acc = priv_key_account(BTCTEST, coins_value[BTCTEST][0]['privkey'])
#create_tx(BTCTEST,btc_acc, coins[BTCTEST][1]['address']), 0.000001)
send_tx(BTCTEST, btc_acc, coins_value[BTCTEST][1]['address'], 0.000001)

# ethTEST Transaction
coins_value = coins()
#print (coins_value [BTCTEST][0]['privkey'])
#account = priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey'])
eth_acc = priv_key_account(ETH, coins_value[ETH][0]['privkey'])
#create_tx(BTCTEST,btc_acc, coins[BTCTEST][1]['address']), 0.000001)
send_tx(ETH, eth_acc, coins_value[ETH][1]['address'], 0.000001)


#Call to Derive Wallets
coins_1 = {
    ETH: derive_wallets(coin=ETH),
    BTC: derive_wallets(coin=BTC),
}
#pprint(coins())

