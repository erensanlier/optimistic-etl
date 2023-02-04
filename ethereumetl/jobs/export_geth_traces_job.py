# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.export_traces_job import calculate_trace_indexes
from ethereumetl.json_rpc_requests import generate_geth_trace_block_by_number_json_rpc
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.geth_trace_mapper import EthGethTraceMapper
from ethereumetl.mappers.trace_mapper import EthTraceMapper
from ethereumetl.service.trace_id_calculator import calculate_trace_ids
from ethereumetl.service.trace_status_calculator import calculate_trace_statuses
from ethereumetl.utils import validate_range, rpc_response_to_result
from collections import defaultdict


# Exports geth traces
class ExportGethTracesJob(BaseJob):
    def __init__(
            self,
            transactions_iterable,
            batch_size,
            web3_provider,
            max_workers,
            item_exporter):
        self.trace_mapper = EthTraceMapper()
        self.transactions_iterable = transactions_iterable

        self.web3_provider = web3_provider

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.geth_trace_mapper = EthGethTraceMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            self.transactions_iterable,
            self._export_batch,
        )

    def _export_batch(self, transactions):
        # TODO: Change to len(block_number_batch) > 0 when this issue is fixed
        # print(transactions)

        def group_by_key(arr, key):
            groups = defaultdict(list)
            for item in arr:
                groups[item[key]].append(item)
            return dict(groups)

        grouped_transactions = group_by_key(transactions, 'block_number')

        all_traces = []

        for block_number, block_transactions in grouped_transactions.items():
            trace_block_rpc = generate_geth_trace_block_by_number_json_rpc(block_number)
            response = self.web3_provider.make_request(method=trace_block_rpc['method'],
                                                       params=trace_block_rpc['params'])
            result = rpc_response_to_result(response)
            geth_trace = self.geth_trace_mapper.json_dict_to_geth_trace({
                'block_number': block_number,
                'transaction_traces': [tx_trace.get('result') for tx_trace in result],
            })

            traces = self.geth_trace_mapper.geth_trace_to_trace_list(geth_trace, block_transactions)
            all_traces.extend(traces)

        calculate_trace_statuses(all_traces)
        calculate_trace_ids(all_traces)
        calculate_trace_indexes(all_traces)
        
        for trace in all_traces:
            self.item_exporter.export_item(self.trace_mapper.trace_to_dict(trace))

        # print("Result:")
        # print(result)

        # print("Geth Trace:")
        # traces = self.geth_trace_mapper.geth_trace_to_dict(geth_trace)
        # print(traces)
        # self.item_exporter.export_item(traces)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
