---
layout: default
title: Warehouse types
parent: Documentation
nav_order: 4
---

# Warehouse types

Warehouses are configured as part of a [Soda warehouse configuration file]({% link documentation/warehouse.md %}).
This section defines the available connection properties for each warehouse type:

- [Snowflake](#snowflake)
- [AWS Athena](#aws-athena)
- [GCP BigQuery](#gcp-bigquery)
- [PostgreSQL](#postgresql)
- [Redshift](#redshift)
- [Microsoft SQLServer](#sqlserver)
- [Spark SQL](#sparks-sql)

## Snowflake

<sub>Example configuration</sub>
```yaml
name: my_snowflake_project
connection:
    type: snowflake
    username: env_var(SNOWFLAKE_USERNAME)
    password: env_var(SNOWFLAKE_PASSWORD)
    account: YOUR_SNOWFLAKE_ACCOUNT.eu-west-1
    warehouse: YOUR_WAREHOUSE
    database: YOUR_DATABASE
    schema: PUBLIC
...
```

| Property | Description | Required |
| -------- | ----------- | -------- |
| type | `snowflake` | Required |
| username |  | Required |
| password |  | Required |
| account | Eg YOUR_SNOWFLAKE_ACCOUNT.eu-west-1 | Required |
| warehouse |  | Required |
| database |  | Required |
| schema |  | Required |

## AWS Athena

<sub>Example configuration</sub>

```yaml
name: my_athena_project
connection:
    type: athena
    database: sodalite_test
    access_key_id: env_var(AWS_ACCESS_KEY_ID)
    secret_access_key: env_var(AWS_SECRET_ACCESS_KEY)
    role_arn: an optional IAM role arn to be assumed
    region: eu-west-1
    staging_dir: <YOUR STAGING PATH IN AWS S3>
...
```

## GCP BigQuery

<sub>Example configuration</sub>

```yaml
name: my_bigquery_project
connection:
    type: bigquery
    account_info: <PATH TO YOUR BIGQUERY ACCOUNT INFO JSON FILE>
    dataset: sodasql
...
```

## PostgreSQL

<sub>Example configuration</sub>

```yaml
name: my_postgres_project
connection:
    type: postgres
    host: localhost
    username: sodasql
    password: sodasql
    database: sodasql
    schema: public
...
```

## Redshift

<sub>Example configuration</sub>

```yaml
name: my_redshift_project
connection:
    type: redshift
    host: <YOUR AWS REDSHIFT HOSTNAME>
    username: soda
    password: <YOUR AWS REDSHIFT PASSWORD>
    database: soda_agent_test
    schema: public
    access_key_id: env_var(AWS_ACCESS_KEY_ID)
    secret_access_key: env_var(AWS_SECRET_ACCESS_KEY)
    role_arn: an optional IAM role arn to be assumed
    region: eu-west-1
...
```

## Microsoft SQLServer (Experimental)

<sub>Example configuration</sub>

```yaml
name: my_sqlserver_project
connection:
  type: sqlserver
  host: <YOUR SQLServer HOSTNAME>
  username: env_var(SQL_SERVER_USERNAME)
  password: env_var(SQL_SERVER_PASSWORD)
  database: master
  schema: dbo
```
## Spark SQL

_Coming soon_
