# Import dependencies
import subprocess
import json
import os

from dotenv import load_dotenv

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants.py import *
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
#from eth_account import Account
from web3 import Web3, middleware, Account

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = './derive -g --mnemonic={mnemonic} --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# # Create a dictionary object called coins to store the output from `derive_wallets`.
def coins():
    coin_dict = {
        'btc' : derive_wallets(mnemonic, BTC, 3),
        'eth' : derive_wallets(mnemonic, ETH, 3)
        'btc-test' : derive_wallets(mnemonic, BTCTEST, 3),
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
# btc_acc = priv_key_account(BTCTEST, priv_key='cPATqqavHDLmsLX2Ej7SR5gvF3u9QJHLAC7taSQEcSuYucC6NGnG')
# create_tx(BTCTEST,btc_acc,"mmPmSpyY8JFvr6JPF1xv4Xae5k7GwXvouS", 0.000001)
# send_tx(BTCTEST, btc_acc, 'mfkGhz6m2tMwETDU6sgEHY2gp2qcuHaioH', 0.000001)

