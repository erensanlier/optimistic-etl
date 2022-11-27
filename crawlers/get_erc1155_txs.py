from web3 import Web3
import yaml
import csv

from ethereumetl.service.erc1155_transfer_extractor import EthERC1155TransferExtractor
transactions = [
    "0x42c82ab046e89094e05bc67076ab512d3c816de70da2b1c21e9c19647a33690b", #TransferBatch with 4
    "0x247e793635ff121dc2500564c7f9c81fbeb8063859428a77da46cc44f5cf515c", #TransferBatch with 1
    "0xdb7f3b73eb17ea2ef818a1649c77c4f5b81451f564508f55667c58bf356a2816", #TransferSingle
]

TRANSFER_SINGLE_EVENT_TOPIC = '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62'
TRANSFER_BATCH_EVENT_TOPIC = '0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb'

# read secrets.yaml
with open("../secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)
    RPC_ENDPOINT = secrets['infura_rpc']
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
txs = []
for transaction in transactions:
    txs.append(dict(w3.eth.get_transaction_receipt(transaction)))

class EthReceiptLog(object):
    def __init__(self):
        self.log_index = None
        self.transaction_hash = None
        self.transaction_index = None
        self.block_hash = None
        self.block_number = None
        self.address = None
        self.data = None
        self.topics = []
def extract_log_data(receipts):
    points = []
    for receipt in receipts:
        for log in receipt['logs']:
            topic_zero = (w3.toHex(log['topics'][0]))
            if topic_zero == TRANSFER_BATCH_EVENT_TOPIC or topic_zero == TRANSFER_SINGLE_EVENT_TOPIC:
                receipt_log = EthReceiptLog()
                receipt_log.address = log['address']
                receipt_log.log_index = log['logIndex']
                receipt_log.block_number = log['blockNumber']
                receipt_log.block_hash = w3.toHex(log['blockHash'])
                receipt_log.topics = [w3.toHex(topic) for topic in log['topics']]
                receipt_log.transaction_index = log['transactionIndex']
                receipt_log.data = log['data']
                receipt_log.transaction_hash = w3.toHex(log['transactionHash'])

                points.append(receipt_log)
    return points

receipts = extract_log_data(txs)
#write receipts to a csv file
with open('erc1155_txs.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['log_index','transaction_hash','transaction_index','block_hash','block_number','address','data','topics'])
    for receipt in receipts:
        writer.writerow([receipt.log_index,receipt.transaction_hash,receipt.transaction_index,receipt.block_hash,receipt.block_number,receipt.address,receipt.data,receipt.topics])

# process receipts with erc1155_transfers_item_exporter
for receipt in receipts:
    transfers =  EthERC1155TransferExtractor().extract_transfer_from_log(receipt)
    # write the transfer to a csv file
    with open('erc1155_transfers.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        # write header
        if csvfile.tell() == 0:
            writer.writerow(['token_address', 'operator','from_address','to_address','id','value','block_number','transaction_hash','log_index'])
        # for every transfer in transfers, write to csv
        for transfer in transfers:
            writer.writerow([transfer.token_address, transfer.operator, transfer.token_address,transfer.from_address,transfer.to_address,transfer.id,transfer.value,transfer.block_number,transfer.transaction_hash,transfer.log_index])