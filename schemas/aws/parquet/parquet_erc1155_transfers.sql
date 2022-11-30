CREATE EXTERNAL TABLE IF NOT EXISTS parquet_erc1155_transfers (
    token_address STRING,
    operator STRING,
    from_address STRING,
    to_address STRING,
    id DECIMAL(38,0),
    value DECIMAL(38,0),
    transaction_hash STRING,
    log_index BIGINT,
    block_number BIGINT
)
PARTITIONED BY (start_block BIGINT, end_block BIGINT)
STORED AS PARQUET
LOCATION 's3://<your_bucket>/ethereumetl/parquet/erc1155_transfers';

MSCK REPAIR TABLE parquet_erc1155_transfers;