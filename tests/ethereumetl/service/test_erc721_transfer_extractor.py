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
from ethereumetl.service.erc721_transfer_extractor import EthERC721TransferExtractor

erc721_transfer_extractor = EthERC721TransferExtractor()


def test_extract_transfer_from_receipt_log():
    log = EthReceiptLog()
    log.address = '0x25c6413359059694A7FCa8e599Ae39Ce1C944Da2'
    log.block_number = 1061946
    log.data = '0x'
    log.log_index = 0
    log.topics = ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
                  '0x000000000000000000000000e9eeaec75883f0e389a78e2260bfac1776df2f1d',
                  '0x0000000000000000000000000000000000000000000000000000000000000000',
                  '0xfad']
    log.transaction_hash = '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'

    erc721_transfer = erc721_transfer_extractor.extract_transfer_from_log(log)

    assert erc721_transfer.token_address == '0x25c6413359059694a7fca8e599ae39ce1c944da2'
    assert erc721_transfer.from_address == '0xe9eeaec75883f0e389a78e2260bfac1776df2f1d'
    assert erc721_transfer.to_address == '0x0000000000000000000000000000000000000000'
    assert erc721_transfer.token_id == 4013 #hex(0xfad) = 4013
    assert erc721_transfer.transaction_hash == '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    assert erc721_transfer.block_number == 1061946
test_extract_transfer_from_receipt_log()
