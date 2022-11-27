# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
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


import logging
from builtins import map

from ethereumetl.domain.erc1155_transfer import EthERC1155Transfer
from ethereumetl.utils import chunk_string, hex_to_dec, to_normalized_address

# https://ethereum.stackexchange.com/questions/12553/understanding-logs-and-log-blooms
# https://docs.openzeppelin.com/contracts/3.x/api/token/erc1155#IERC1155-TransferSingle-address-address-address-uint256-uint256-
TRANSFER_EVENT_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
TRANSFER_SINGLE_EVENT_TOPIC = '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62'
TRANSFER_BATCH_EVENT_TOPIC = '0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb'
logger = logging.getLogger(__name__)


class EthERC1155TransferExtractor(object):
    def extract_transfer_from_log(self, receipt_log):

        topics = receipt_log.topics
        if topics is None or len(topics) < 1:
            # This is normal, topics can be empty for anonymous events
            return None

        # ERC 1155 tokens can emmit two different transfer events:
        #   TransferSingle: A single token or value in a transaction
        #   TransferBatch: An array of tokens and an array of values in a transaction
        # Either of these events have 6 topics in total, data packs 2 of them.
        if ((topics[0]).casefold() == TRANSFER_SINGLE_EVENT_TOPIC or (topics[0]).casefold() == TRANSFER_BATCH_EVENT_TOPIC) and len(topics) == 4:
            # Handle unindexed event fields
            topics_with_data = topics + split_to_words(receipt_log.data) # two events from unpacking two arrays
            # if the number of topics and fields in data part != 6, then it's a weird event
            if (topics[0]).casefold() == TRANSFER_SINGLE_EVENT_TOPIC and len(topics_with_data) != 6 or (topics[0]).casefold() == TRANSFER_BATCH_EVENT_TOPIC and len(topics_with_data) <= 6:
                logger.warning("The number of topics and data parts is not equal to 6 in log {} of transaction {}"
                               .format(receipt_log.log_index, receipt_log.transaction_hash))
                return None
            erc1155_transfer = EthERC1155Transfer()
            erc1155_transfer.token_address = to_normalized_address(receipt_log.address)
            erc1155_transfer.operator = word_to_address(topics_with_data[1])
            erc1155_transfer.from_address = word_to_address(topics_with_data[2])
            erc1155_transfer.to_address = word_to_address(topics_with_data[3])
            erc1155_transfer.transaction_hash = receipt_log.transaction_hash
            erc1155_transfer.log_index = receipt_log.log_index
            erc1155_transfer.block_number = receipt_log.block_number
            if (topics[0]).casefold() == TRANSFER_SINGLE_EVENT_TOPIC:
                erc1155_transfer.ids = [hex_to_dec(topics_with_data[4])]
                erc1155_transfer.values = [hex_to_dec(topics_with_data[5])]
                return [erc1155_transfer]
            else: # by default this is a TransferBatch
                # half of them token id's, remaining half how many of them have been transferred in the transaction
                # thus, total_items is always even, we don't have to worry about division immediately.
                # packing of the array as follows:
                # | 4 items about the event | data unpacked |
                # | 0                       | 4                    | 6 | 7 + k                                  | 8 +k                                      |
                # | 4 items about the event | 2 items for packing | number of items in the first array | items | number of items in the next array | items |
                transactions = []
                total_items = int((len(topics_with_data[6:]) - 2) / 2)
                ids = [hex_to_dec(item) for item in topics_with_data[7: 7+total_items]]
                values = [hex_to_dec(item) for item in topics_with_data[8+total_items:]]
                total_transfer = dict()
                for pair in list(zip(ids,values)):
                    if pair[0] in total_transfer.keys():
                        total_transfer[pair[0]] += pair[1]
                    else:
                        total_transfer[pair[0]] = pair[1]
                for key in total_transfer.keys():
                    base_tx = erc1155_transfer
                    base_tx.id = key
                    base_tx.value = total_transfer[key]
                    transactions.append(base_tx)
                return transactions
        return None


def split_to_words(data):
    if data and len(data) > 2:
        data_without_0x = data[2:]
        words = list(chunk_string(data_without_0x, 64))
        words_with_0x = list(map(lambda word: '0x' + word, words))
        return words_with_0x
    return []


def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)
