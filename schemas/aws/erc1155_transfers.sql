CREATE EXTERNAL TABLE IF NOT EXISTS erc1155_transfers (
    token_address STRING,
    from_address STRING,
    to_address STRING,
    token_id STRING,
    transaction_hash STRING,
    log_index BIGINT,
    block_number BIGINT
)
PARTITIONED BY (block_date STRING)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://<your_bucket>/export/erc1155_transfers/';

MSCK REPAIR TABLE erc1155_transfers;
