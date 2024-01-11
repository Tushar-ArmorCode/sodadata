import logging
from textwrap import dedent

from helpers.common_test_tables import customers_test_table
from helpers.data_source_fixture import DataSourceFixture
from soda.contracts.connection import Connection
from soda.contracts.contract import Contract, ContractResult
from soda.contracts.exceptions import SodaException
from soda.contracts.soda_cloud import SodaCloud


def test_contract_api(data_source_fixture: DataSourceFixture):
    table_name = data_source_fixture.ensure_test_table(customers_test_table)

    soda_cloud_yaml_str = dedent("""
        api_key_id: ${SODA_CLOUD_API_KEY_ID}
        api_key_secret: ${SODA_CLOUD_API_KEY_SECRET}
    """)

    connection_yaml_str = dedent("""
        type: postgres
        host: localhost
        database: sodasql
        username: sodasql
        password: ${POSTGRES_PWD}
    """)

    contract_yaml_str = dedent(f"""
      schema: {data_source_fixture.schema_name}
      dataset: {table_name}
      columns:
      - name: id
        data_type: text
        unique: true
        attributes:
          pii: sensitive
      - name: cst_size
        data_type: numeric
      - name: cst_size_txt
        valid_values: [1, 2, 3]
      - name: distance
        data_type: integer
      - name: pct
      - name: cat
      - name: country
        data_type: number
        not_null: true
      - name: zip
      - name: email
      - name: date_updated
        data_type: date
      - name: ts
      - name: ts_with_tz
    """)

    try:
        soda_cloud: SodaCloud = SodaCloud.from_yaml_str(soda_cloud_yaml_str)
        with Connection.from_yaml_str(connection_yaml_str) as connection:
            contract: Contract = Contract.from_yaml_str(contract_yaml_str)
            contract_result: ContractResult = contract.verify(connection, soda_cloud)
            # optionally do something with the contract verification result
            logging.debug(f"Contract verification passed:\n{contract_result.get_text_report()}")

    except SodaException as e:
        logging.exception(f"Contract verification failed:\n{e.get_text_report()}")
