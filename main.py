from web3 import Web3
import time
from tqdm import tqdm
from loguru import logger
import pandas as pd

from config import *
def check_status_tx(tx_hash,w3):

    logger.info(f'waiting for confirmation transaction https://etherscan.io/tx/{w3.to_hex(tx_hash)}...')
    while True:
        try:
            status = w3.eth.get_transaction_receipt(tx_hash)
            status = status['status']
            if status in [0, 1]:
                return status
            time.sleep(1)
        except Exception as error:
            time.sleep(1)
def sleep_indicator(secs):
    for i in tqdm(range(secs), desc='wait', bar_format="{desc}: {n_fmt}s / {total_fmt}s {bar}", colour='green'):
        time.sleep(1)

def mint(privatekey):
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/zksync2-era'))
    account = w3.eth.account.from_key(privatekey)
    address = account.address

    data = '0x1249c58b'
    try:
        tx = {
            'from': address,
            'to': Web3.to_checksum_address('0x1ec43b024A1C8D084BcfEB2c0548b6661C528dfA'),
            'value': 0,
            'nonce': w3.eth.get_transaction_count(address),
            'data': data,
            'chainId': w3.eth.chain_id,
            'gasPrice': w3.eth.gas_price
        }

        tx['gas'] = w3.eth.estimate_gas(tx)
        sign = account.sign_transaction(tx)
        hash = w3.eth.send_raw_transaction(sign.rawTransaction)
        status = check_status_tx(hash, w3)
        if status == 1:
            logger.success(f'{address} - успешно заминтил: https://explorer.zksync.io/tx/{w3.to_hex(hash)}...')
            sleep_indicator(random.randint(delay[0], delay[1]))
            return address, 'success'

    except Exception as e:
        logger.error(e)
        return address, 'error'

def main():
    print(f'\n{" " * 32}автор - https://t.me/iliocka{" " * 32}\n')
    wallets, results = [],[]
    for key in keys:
        res = mint(key)
        wallets.append(res[0]), results.append(res[1])
    logger.success(f'Успешный mинетинг на {len(keys)} кошельков, таблица с резами загружена...')
    res = {'address': wallets, 'result': results}
    df = pd.DataFrame(res)
    df.to_csv('results.csv',mode='a', index=False)
    print(f'\n{" " * 32}donate - EVM 0xFD6594D11b13C6b1756E328cc13aC26742dBa868{" " * 32}\n')
    print(f'\n{" " * 32}donate - trc20 TMmL915TX2CAPkh9SgF31U4Trr32NStRBp{" " * 32}\n')

if __name__ == '__main__':
    main()