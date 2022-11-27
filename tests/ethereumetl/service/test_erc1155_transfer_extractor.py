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


from ethereumetl.domain.receipt_log import EthReceiptLog
from ethereumetl.service.erc1155_transfer_extractor import EthERC1155TransferExtractor

erc1155_transfer_extractor = EthERC1155TransferExtractor()


def test_extract_transfer_single_from_receipt_log():
    log = EthReceiptLog()
    log.address = '0x5351105753bdbc3baa908a0c04f1468535749c3d'
    log.block_number = 11681009
    log.data = '0x00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000014'
    log.log_index = 0
    log.topics = ['0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62',
                  '0x000000000000000000000000ab3e5a900663ea8c573b8f893d540d331fbab9f5',
                  '0x0000000000000000000000000000000000000000000000000000000000000000',
                  '0x000000000000000000000000ab3e5a900663ea8c573b8f893d540d331fbab9f5']
    log.transaction_hash = '0xdb7f3b73eb17ea2ef818a1649c77c4f5b81451f564508f55667c58bf356a2816'

    erc1155_transfer = erc1155_transfer_extractor.extract_transfer_from_log(log)


    assert erc1155_transfer.token_address == '0x5351105753bdbc3baa908a0c04f1468535749c3d'
    assert erc1155_transfer.operator == '0xab3e5a900663ea8c573b8f893d540d331fbab9f5'
    assert erc1155_transfer.from_address == '0x0000000000000000000000000000000000000000'
    assert erc1155_transfer.to_address == '0xab3e5a900663ea8c573b8f893d540d331fbab9f5'
    assert erc1155_transfer.ids == [1]
    assert erc1155_transfer.values == [20]
    assert erc1155_transfer.transaction_hash == '0xdb7f3b73eb17ea2ef818a1649c77c4f5b81451f564508f55667c58bf356a2816'
    assert erc1155_transfer.block_number == 11681009

def test_extract_transfer_batch_from_receipt_log():
    log = EthReceiptLog()
    log.address = '0xc36cf0cfcb5d905b8b513860db0cfe63f6cf9f5c'
    log.block_number = 16059982
    log.data = '0x000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000005b200000000000000000000000000000000000000000000000000000000000005b600000000000000000000000000000000000000000000000000000000000005b900000000000000000000000000000000000000000000000000000000000005b60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001'
    log.log_index = 0
    log.topics = ['0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb',
                  '0x00000000000000000000000037b94141bca7000241b87b4b361f155197181002',
                  '0x000000000000000000000000381e840f4ebe33d0153e9a312105554594a98c42',
                  '0x00000000000000000000000090ba4568010b0fc7739c1b785af08438b6275e08']
    log.transaction_hash = '0x35adcfb1a1a69e3cae18c4b23cf30a62a3278aa704e32fe558b12c474a3f8d3e'

    erc1155_transfer = erc1155_transfer_extractor.extract_transfer_from_log(log)
    expected_id_list = [496131690970728279729600177635518052302848,
                        497492820438412033583453676065245125148672,
                        498513667539174848973843799887540429783040,
                        497492820438412033583453676065245125148672]
    expected_value_list = [1,1,1,1]

    assert erc1155_transfer.token_address == '0xc36cf0cfcb5d905b8b513860db0cfe63f6cf9f5c'
    assert erc1155_transfer.operator == '0x37b94141bca7000241b87b4b361f155197181002'
    assert erc1155_transfer.from_address == '0x381e840f4ebe33d0153e9a312105554594a98c42'
    assert erc1155_transfer.to_address == '0x90ba4568010b0fc7739c1b785af08438b6275e08'
    assert erc1155_transfer.ids == expected_id_list
    assert erc1155_transfer.values == expected_value_list
    assert erc1155_transfer.transaction_hash == '0x35adcfb1a1a69e3cae18c4b23cf30a62a3278aa704e32fe558b12c474a3f8d3e'
    assert erc1155_transfer.block_number == 16059982
