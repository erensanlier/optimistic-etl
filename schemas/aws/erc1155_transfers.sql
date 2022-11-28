CREATE EXTERNAL TABLE IF NOT EXISTS erc1155_transfers (
    token_address STRING,
    operator STRING,
    from_address STRING,
    to_address STRING,
    id STRING,
    value STRING,
    transaction_hash STRING,
    log_index BIGINT,
    block_number BIGINT
)
PARTITIONED BY (block_date STRING)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://<your_bucket>/export/erc1155_transfers/';

MSCK REPAIR TABLE erc1155_transfers;
