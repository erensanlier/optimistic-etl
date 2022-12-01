import yaml
from web3 import Web3

with open("../secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)
    RPC_ENDPOINT = secrets['alchemy_rpc']
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))

from ethereumetl.jobs.export_traces_job import ExportTracesJob

from ethereumetl.jobs.exporters.traces_item_exporter import traces_item_exporter



start_block = 1755634
end_block = 1755635

job = ExportTracesJob(
    start_block=start_block,
    end_block=end_block,
    batch_size=2,
    max_workers=5,
    web3=w3,
    item_exporter=traces_item_exporter('traces.csv'),
)
job.run()
# convert csv lines to json objects written to expected_traces_in_json.csv
import json
import csv
with open("traces.csv", "r") as f:
    reader = csv.DictReader(f)
    # dump every line as a json object and seperate by newline in a new file
    with open("../tests/resources/test_stream/blocks_1755634_1755635/expected_traces.json", "w") as f2:
        for row in reader:
            json.dump(row, f2)
            f2.write('\n')
with open("../tests/resources/test_stream/blocks_1755634_1755635/expected_traces.json", "r") as f:
    with open("../tests/resources/test_stream/blocks_1755634_1755635/expected_traces.json", "w") as f2:
        for line in f:
            f2.write(line.replace('""', 'null'))