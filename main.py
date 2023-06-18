from web3 import Web3
import time
from tqdm import tqdm
from loguru import logger
import pandas as pd

from config import *


def check_status_tx(w3, tx_hash):
    logger.info(f'жду подтверждения транзакции - https://explorer.zksync.io/tx/{w3.to_hex(tx_hash)}...')

    start_time = int(time.time())
    while True:
        current_time = int(time.time())
        if current_time >= start_time + 100:
            logger.info('транзакция не подтвердилась за 100 cекунд, начинаю повторную отправку...')
            return 0
        try:
            status = w3.eth.get_transaction_receipt(tx_hash)['status']
            if status == 1:
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
        hash_ = w3.eth.send_raw_transaction(sign.rawTransaction)
        status = check_status_tx(w3, hash_)
        if status == 1:
            logger.success(f'{address} - успешно заминтил: https://explorer.zksync.io/tx/{w3.to_hex(hash_)}...')
            sleep_indicator(random.randint(delay[0], delay[1]))
            return address, 'success'
        else:
            logger.info(f'{address} - пробую еще раз...')
            mint(privatekey)

    except Exception as e:
        error = str(e)
        if "insufficient funds for gas * price + value" in error:
            logger.error(f'{address} - нет баланса нативного токена')
            return address, 'error'
        elif "Already minted" in error:
            logger.info(f'{address} - уже заминчено')
            return address, 'already minted'
        else:
            logger.error(e)
            return address, 'error'


def main():
    print(f'\n{" " * 32}автор - https://t.me/iliocka{" " * 32}\n')
    wallets, results = [], []
    for key in keys:
        res = mint(key)
        wallets.append(res[0]), results.append(res[1])
    logger.success(f'Успешный mинетинг на {len(keys)} кошельков, таблица с резами загружена...')
    res = {'address': wallets, 'result': results}
    df = pd.DataFrame(res)
    df.to_csv('results.csv', mode='a', index=False)
    print(f'\n{" " * 32}donate - EVM 0xFD6594D11b13C6b1756E328cc13aC26742dBa868{" " * 32}\n')
    print(f'\n{" " * 32}donate - trc20 TMmL915TX2CAPkh9SgF31U4Trr32NStRBp{" " * 32}\n')


if __name__ == '__main__':
    main()
