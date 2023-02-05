import logging

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from ethereumetl.enumeration.entity_type import EntityType
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_traces_job import ExportTracesJob
from ethereumetl.jobs.export_geth_traces_job import ExportGethTracesJob
from ethereumetl.jobs.extract_contracts_job import ExtractContractsJob
from ethereumetl.jobs.extract_erc1155_transfers_job import ExtractERC1155TransfersJob
from ethereumetl.jobs.extract_erc20_tokens_job import ExtractERC20TokensJob
from ethereumetl.jobs.extract_erc20_transfers_job import ExtractERC20TransfersJob
from ethereumetl.jobs.extract_erc721_tokens_job import ExtractERC721TokensJob
from ethereumetl.jobs.extract_erc721_transfers_job import ExtractERC721TransfersJob
from ethereumetl.jobs.extract_erc1155_tokens_job import ExtractERC1155TokensJob
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from ethereumetl.jobs.extract_tokens_job import ExtractTokensJob
from ethereumetl.streaming.enrich import enrich_transactions, enrich_logs, enrich_traces, \
    enrich_contracts, enrich_tokens, enrich_erc20_transfers, enrich_erc721_transfers, enrich_erc1155_transfers, \
    enrich_erc20_tokens, enrich_erc721_tokens, enrich_erc1155_tokens
from ethereumetl.streaming.eth_item_id_calculator import EthItemIdCalculator
from ethereumetl.streaming.eth_item_timestamp_calculator import EthItemTimestampCalculator
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import build_web3


class EthStreamerAdapter:
    def __init__(
            self,
            web3_provider,
            batch_web3_provider,
            item_exporter=ConsoleItemExporter(),
            batch_size=100,
            max_workers=5,
            entity_types=tuple(EntityType.ALL_FOR_STREAMING)):
        self.web3_provider = web3_provider
        self.batch_web3_provider = batch_web3_provider
        self.item_exporter = item_exporter
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.entity_types = entity_types
        self.item_id_calculator = EthItemIdCalculator()
        self.item_timestamp_calculator = EthItemTimestampCalculator()

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self):
        w3 = build_web3(self.batch_web3_provider)
        return int(w3.eth.get_block("latest").number)

    def export_all(self, start_block, end_block):
        # Export blocks and transactions
        blocks, transactions = [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(EntityType.TRANSACTION):
            blocks, transactions = self._export_blocks_and_transactions(start_block, end_block)

        # Export receipts and logs
        receipts, logs = [], []
        if self._should_export(EntityType.RECEIPT) or self._should_export(EntityType.LOG):
            receipts, logs = self._export_receipts_and_logs(transactions)

        # Extract token transfers
        # token_transfers = []
        # if self._should_export(EntityType.TOKEN_TRANSFER):
        #     token_transfers = self._extract_token_transfers(logs)

        # Extract ERC20 transfers
        erc20_transfers = []
        if self._should_export(EntityType.ERC20_TRANSFER):
            erc20_transfers = self._export_erc20_transfers(logs)

        # Extract ERC721 transfers
        erc721_transfers = []
        if self._should_export(EntityType.ERC721_TRANSFER):
            erc721_transfers = self._export_erc721_transfers(logs)

        # Extract ERC1155 transfers
        erc1155_transfers = []
        if self._should_export(EntityType.ERC1155_TRANSFER):
            erc1155_transfers = self._export_erc1155_transfers(logs)

        # Export traces (but geth for Optimism)
        traces = []
        if self._should_export(EntityType.TRACE):
            traces = self._export_geth_traces(transactions)

        # Export contracts
        contracts = []
        if self._should_export(EntityType.CONTRACT):
            contracts = self._export_contracts(traces)

        # Export tokens
        # tokens = []
        # if self._should_export(EntityType.TOKEN):
        #     tokens = self._extract_tokens(contracts)

        erc20_tokens = []
        if self._should_export(EntityType.ERC20_TOKEN):
            erc20_tokens = self._export_erc20_tokens(contracts)

        erc721_tokens = []
        if self._should_export(EntityType.ERC721_TOKEN):
            erc721_tokens = self._export_erc721_tokens(contracts)

        erc1155_tokens = []
        if self._should_export(EntityType.ERC1155_TOKEN):
            erc1155_tokens = self._export_erc1155_tokens(contracts)

        enriched_blocks = blocks \
            if EntityType.BLOCK in self.entity_types else []
        # Added L1 enrichments
        enriched_transactions = enrich_transactions(transactions, receipts) \
            if EntityType.TRANSACTION in self.entity_types else []
        enriched_logs = enrich_logs(blocks, logs) \
            if EntityType.LOG in self.entity_types else []
        # enriched_token_transfers = enrich_token_transfers(blocks, token_transfers) \
        #     if EntityType.TOKEN_TRANSFER in self.entity_types else []
        enriched_erc20_transfers = enrich_erc20_transfers(blocks, erc20_transfers) \
            if EntityType.ERC20_TRANSFER in self.entity_types else []
        enriched_erc721_transfers = enrich_erc721_transfers(blocks, erc721_transfers) \
            if EntityType.ERC721_TRANSFER in self.entity_types else []
        enriched_erc1155_transfers = enrich_erc1155_transfers(blocks, erc1155_transfers) \
            if EntityType.ERC1155_TRANSFER in self.entity_types else []
        enriched_traces = enrich_traces(blocks, traces) \
            if EntityType.TRACE in self.entity_types else []
        enriched_contracts = enrich_contracts(blocks, contracts) \
            if EntityType.CONTRACT in self.entity_types else []
        enriched_erc20_tokens = enrich_erc20_tokens(blocks, erc20_tokens) \
            if EntityType.ERC20_TOKEN in self.entity_types else []
        enriched_erc721_tokens = enrich_erc721_tokens(blocks, erc721_tokens) \
            if EntityType.ERC721_TOKEN in self.entity_types else []
        enriched_erc1155_tokens = enrich_erc1155_tokens(blocks, erc1155_tokens) \
            if EntityType.ERC1155_TOKEN in self.entity_types else []
        # enriched_tokens = enrich_tokens(blocks, tokens) \
        #     if EntityType.TOKEN in self.entity_types else []
        logging.info('Exporting with ' + type(self.item_exporter).__name__)

        all_items = \
            sort_by(enriched_blocks, 'number') + \
            sort_by(enriched_transactions, ('block_number', 'transaction_index')) + \
            sort_by(enriched_logs, ('block_number', 'log_index')) + \
            sort_by(enriched_erc20_transfers, ('block_number', 'log_index')) + \
            sort_by(enriched_erc721_transfers, ('block_number', 'log_index')) + \
            sort_by(enriched_erc1155_transfers, ('block_number', 'log_index')) + \
            sort_by(enriched_traces, ('block_number', 'trace_index')) + \
            sort_by(enriched_contracts, ('block_number',)) + \
            sort_by(enriched_erc20_tokens, ('block_number', 'log_index')) + \
            sort_by(enriched_erc721_tokens, ('block_number', 'log_index')) + \
            sort_by(enriched_erc1155_tokens, ('block_number', 'log_index'))
        # sort_by(enriched_token_transfers, ('block_number', 'log_index')) + \
        # sort_by(enriched_tokens, ('block_number',)) + \
        self.calculate_item_ids(all_items)
        self.calculate_item_timestamps(all_items)

        self.item_exporter.export_items(all_items)

    def _export_blocks_and_transactions(self, start_block, end_block):
        blocks_and_transactions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION)
        )
        blocks_and_transactions_job.run()
        blocks = blocks_and_transactions_item_exporter.get_items('block')
        transactions = blocks_and_transactions_item_exporter.get_items('transaction')
        return blocks, transactions

    def _export_receipts_and_logs(self, transactions):
        exporter = InMemoryItemExporter(item_types=['receipt', 'log'])
        job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction['hash'] for transaction in transactions),
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter,
            export_receipts=self._should_export(EntityType.RECEIPT),
            export_logs=self._should_export(EntityType.LOG)
        )
        job.run()
        receipts = exporter.get_items('receipt')
        logs = exporter.get_items('log')
        return receipts, logs

    def _export_token_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['token_transfer'])
        job = ExtractTokenTransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        token_transfers = exporter.get_items('token_transfer')
        return token_transfers

    def _export_erc20_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['erc20_transfer'])
        job = ExtractERC20TransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        erc20_transfers = exporter.get_items('erc20_transfer')
        return erc20_transfers

    def _export_erc721_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['erc721_transfer'])
        job = ExtractERC721TransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        erc721_transfers = exporter.get_items('erc721_transfer')
        return erc721_transfers

    def _export_erc1155_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['erc1155_transfer'])
        job = ExtractERC1155TransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        erc1155_transfers = exporter.get_items('erc1155_transfer')
        return erc1155_transfers

    def _export_traces(self, start_block, end_block):
        exporter = InMemoryItemExporter(item_types=['trace'])
        job = ExportTracesJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        traces = exporter.get_items('trace')
        return traces

    def _export_geth_traces(self, transactions):
        exporter = InMemoryItemExporter(item_types=['trace'])
        job = ExportGethTracesJob(
            transactions_iterable=transactions,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        traces = exporter.get_items('trace')
        return traces

    def _export_contracts(self, traces):
        exporter = InMemoryItemExporter(item_types=['contract'])
        job = ExtractContractsJob(
            traces_iterable=traces,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        contracts = exporter.get_items('contract')
        return contracts

    def _export_tokens(self, contracts):
        exporter = InMemoryItemExporter(item_types=['token'])
        job = ExtractTokensJob(
            contracts_iterable=contracts,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('token')
        return tokens

    def _export_erc20_tokens(self, contracts):
        exporter = InMemoryItemExporter(item_types=['erc20_token'])
        job = ExtractERC20TokensJob(
            contracts_iterable=contracts,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('erc20_token')
        return tokens

    def _export_erc721_tokens(self, contracts):
        exporter = InMemoryItemExporter(item_types=['erc721_token'])
        job = ExtractERC721TokensJob(
            contracts_iterable=contracts,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('erc721_token')
        return tokens

    def _export_erc1155_tokens(self, contracts):
        exporter = InMemoryItemExporter(item_types=['erc1155_token'])
        job = ExtractERC1155TokensJob(
            contracts_iterable=contracts,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('erc1155_token')
        return tokens

    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return True

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.LOG) \
                   or self._should_export(EntityType.TRACE)

        if entity_type == EntityType.RECEIPT:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(
                EntityType.ERC1155_TRANSFER) or self._should_export(EntityType.ERC721_TRANSFER) or self._should_export(
                EntityType.ERC20_TRANSFER) or self._should_export(EntityType.ERC721_TRANSFER)

        if entity_type == EntityType.LOG:
            return EntityType.LOG in self.entity_types or self._should_export(
                EntityType.ERC1155_TRANSFER) or self._should_export(EntityType.ERC721_TRANSFER) or self._should_export(
                EntityType.ERC20_TRANSFER) or self._should_export(EntityType.ERC721_TRANSFER)

        # if entity_type == EntityType.TOKEN_TRANSFER:
        #     return EntityType.TOKEN_TRANSFER in self.entity_types

        if entity_type == EntityType.ERC20_TRANSFER:
            return EntityType.ERC20_TRANSFER in self.entity_types

        if entity_type == EntityType.ERC721_TRANSFER:
            return EntityType.ERC721_TRANSFER in self.entity_types

        if entity_type == EntityType.ERC1155_TRANSFER:
            return EntityType.ERC1155_TRANSFER in self.entity_types

        if entity_type == EntityType.TRACE:
            return EntityType.TRACE in self.entity_types or self._should_export(EntityType.CONTRACT)

        if entity_type == EntityType.CONTRACT:
            return EntityType.CONTRACT in self.entity_types or self._should_export(
                EntityType.ERC20_TOKEN) or self._should_export(EntityType.ERC721_TOKEN) or self._should_export(
                EntityType.ERC1155_TOKEN)

        # if entity_type == EntityType.TOKEN:
        #     return EntityType.TOKEN in self.entity_types

        if entity_type == EntityType.ERC20_TOKEN:
            return EntityType.ERC20_TOKEN in self.entity_types

        if entity_type == EntityType.ERC721_TOKEN:
            return EntityType.ERC721_TOKEN in self.entity_types

        if entity_type == EntityType.ERC1155_TOKEN:
            return EntityType.ERC1155_TOKEN in self.entity_types

        raise ValueError('Unexpected entity type ' + entity_type)

    def calculate_item_ids(self, items):
        for item in items:
            item['item_id'] = self.item_id_calculator.calculate(item)

    def calculate_item_timestamps(self, items):
        for item in items:
            item['item_timestamp'] = self.item_timestamp_calculator.calculate(item)

    def close(self):
        self.item_exporter.close()


def sort_by(arr, fields):
    if isinstance(fields, tuple):
        fields = tuple(fields)
    return sorted(arr, key=lambda item: tuple(item.get(f) for f in fields))
