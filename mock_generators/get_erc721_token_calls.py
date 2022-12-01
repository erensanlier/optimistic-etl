import yaml
from web3 import Web3

with open("../secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)
    RPC_ENDPOINT = secrets['alchemy_rpc']
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))


chain_id = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": "0x1234"
}

# we only need the func_sighashes and call with empty data to any erc721 instance
# get contract
# get sighashes
# transform contract to token(erc721)
# call the required functions with empty data (direct rpc calls ?)
    # maybe this is unnecessary, we can just call the functions directly then map to sighashes ?

from ethereumetl.jobs.export_contracts_job import ExportContractsJob