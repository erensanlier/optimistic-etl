import csv
import json

import yaml
from web3 import Web3

from ethereumetl.service.erc1155_transfer_extractor import EthERC1155TransferExtractor
from get_erc1155_receipt_from_tx import TRANSFER_SINGLE_EVENT_TOPIC, TRANSFER_BATCH_EVENT_TOPIC, extract_log_data

with open("../secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)
    RPC_ENDPOINT = secrets['infura_rpc']
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
block_number = 11093491
transactions = [w3.toHex(tx) for tx in dict(w3.eth.get_block(block_number))['transactions']]
receipts = [w3.eth.get_transaction_receipt(tx) for tx in transactions]

receipts_with_logs = [dict(x) for x in receipts if len(x['logs']) > 0 ]
points = extract_log_data(receipts_with_logs)

receipts_with_relevant_logs = []
for tx_receipt in receipts_with_logs:
    for log in tx_receipt['logs']:
        if w3.toHex(log['topics'][0]) == TRANSFER_SINGLE_EVENT_TOPIC or w3.toHex(log['topics'][0]) == TRANSFER_BATCH_EVENT_TOPIC:
            receipts_with_relevant_logs.append(dict(log))

for receipt in receipts_with_relevant_logs:
    receipt["blockHash"] = w3.toHex(receipt["blockHash"])
    for i in range(len(receipt["topics"])):
        receipt["topics"][i] = w3.toHex(receipt["topics"][i])
    receipt["transactionHash"] = w3.toHex(receipt["transactionHash"])


base_path = "../tests/resources/test_export_erc1155_transfers_job/block_with_transfers/"
logs = "web3_response.eth_getFilterLogs_0x0.json"
uninstall_filter = "web3_response.eth_uninstallFilter_0x0.json"
# TODO: This filter only applies to the single events, use partition to generate two different log files
single_new_filter = f"web3_response.eth_newFilter_fromBlock_{hex(block_number)}_toBlock_{hex(block_number)}_topics_{TRANSFER_SINGLE_EVENT_TOPIC}_{TRANSFER_BATCH_EVENT_TOPIC}.json"
expected_file = "expected_erc1155_transfers.csv"
with open(base_path + logs, "w") as file:
    json_data = {
        "jsonrpc":"2.0",
        "result":receipts_with_relevant_logs,
        "id":1
    }
    json.dump(json_data, file, indent=4)
with open(base_path + uninstall_filter, "w") as file:
    json_data = {
      "jsonrpc": "2.0",
      "result": True,
      "id": 2
    }
    json.dump(json_data, file, indent=4)
with open(base_path + single_new_filter, "w") as file:
    json_data = {
      "jsonrpc": "2.0",
      "result": "0x0",
      "id": 0
    }
    json.dump(json_data, file, indent=4)

for receipt in points:
    transfers =  EthERC1155TransferExtractor().extract_transfer_from_log(receipt)
    # write the transfer to a csv file
    with open(base_path + expected_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        # write header
        if csvfile.tell() == 0:
            writer.writerow(['token_address', 'operator','from_address','to_address','id','value','transaction_hash','log_index', 'block_number'])
        # for every transfer in transfers, write to csv
        for transfer in transfers:
            writer.writerow([transfer.token_address, transfer.operator, transfer.from_address,transfer.to_address,transfer.id,transfer.value,transfer.transaction_hash,transfer.log_index,transfer.block_number])
