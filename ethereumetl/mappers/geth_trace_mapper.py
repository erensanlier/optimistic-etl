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

from ethereumetl.domain.geth_trace import EthGethTrace
from ethereumetl.domain.trace import EthTrace
from ethereumetl.utils import to_normalized_address, hex_to_dec


class EthGethTraceMapper(object):
    def json_dict_to_geth_trace(self, json_dict):
        geth_trace = EthGethTrace()

        geth_trace.block_number = json_dict.get('block_number')
        geth_trace.transaction_traces = json_dict.get('transaction_traces')

        return geth_trace

    def geth_trace_to_dict(self, geth_trace):
        return {
            'type': 'geth_trace',
            'block_number': geth_trace.block_number,
            'transaction_traces': geth_trace.transaction_traces,
        }

    def geth_trace_to_trace_list(self, geth_trace, transaction, parent_type=None, trace_address=None):

        trace = EthTrace()

        trace.block_number = transaction['block_number']
        trace.transaction_hash = transaction['hash']
        trace.transaction_index = transaction['transaction_index']
        trace.subtraces = len(geth_trace.get("calls", []))

        error = geth_trace.get('error')
        if error:
            trace.error = error

        trace_type = geth_trace.get('type')

        if trace_type:
            trace.call_type = trace_type.lower()

        if parent_type:
            trace.trace_type = parent_type.lower()
        else:
            trace.trace_type = trace_type.lower()

        trace.from_address = to_normalized_address(geth_trace.get('from'))
        trace.value = hex_to_dec(geth_trace.get('value'))
        trace.gas = hex_to_dec(geth_trace.get('gas'))
        trace.gas_used = hex_to_dec(geth_trace.get('gasUsed'))

        trace.to_address = to_normalized_address(geth_trace.get('to'))
        trace.input = geth_trace.get('input')
        trace.output = geth_trace.get('output')

        if trace_address is None:
            trace_address = []
            nested_trace_address = []
        else:
            nested_trace_address = trace_address

        trace.trace_address = nested_trace_address

        calls = geth_trace.get("calls", [])

        yield trace

        for idx, call in enumerate(calls):
            yield from self.geth_trace_to_trace_list(call, transaction, trace.trace_type,
                                                     nested_trace_address if trace_address is None else nested_trace_address + [idx])
