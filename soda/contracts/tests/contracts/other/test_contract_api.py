import logging
from textwrap import dedent

from contracts.helpers.contract_test_tables import contracts_test_table
from contracts.helpers.test_connection import TestConnection
from helpers.common_test_tables import customers_test_table
from helpers.data_source_fixture import DataSourceFixture
from soda.contracts.connection import Connection, SodaException
from soda.contracts.contract import Contract, ContractResult
from soda.contracts.soda_cloud import SodaCloud


def test_contract_api(data_source_fixture: DataSourceFixture, environ: dict):
    table_name: str = data_source_fixture.ensure_test_table(contracts_test_table)

    environ["soda_cloud_api_key_id"] = "***"
    environ["soda_cloud_api_key_secret"] = "***"

    connection_yaml_str = dedent("""
        type: postgres
        host: localhost
        database: sodasql
        username: sodasql
        password: ${POSTGRES_PWD}
    """)

    contract_yaml_str = dedent(f"""
      dataset: {table_name}
      columns:
      - name: id
        data_type: text
      - name: size
        data_type: decimal
      - name: distance
        data_type: integer
      - name: created
        data_type: date
    """)

    try:
        # Optionally a Soda Cloud link can be established that
        #  - Enables change-over-time thresholds in checks using the Soda Cloud metric store
        #  - Collects and displays all contract results and diagnostics information
        #  - Central place from which people can subscribe and notifications get dispatched
        soda_cloud: SodaCloud = SodaCloud.from_environment_variables()

        # The connection to the SQL-engine
        with Connection.from_yaml_str(connection_yaml_str) as connection:

            # Parsing the contract YAML into a contract python object
            contract: Contract = Contract.from_yaml_str(contract_yaml_str)

            contract_result: ContractResult = contract.verify(connection, soda_cloud)

            # This place in the code means contract verification has passed successfully:
            # No exceptions means there are no contract execution exceptions and no check failures.

            # The default way to visualize diagnostics information for checks is Soda Cloud.
            # But contract results information can be transformed and sent to any destination
            # (contract_results includes information like eg the check results and diagnostics information)
            logging.debug(f"Contract verification passed:\n{contract_result}")

    except SodaException as e:
        # An exception is raised means there are either contract verification exceptions
        logging.exception(f"Contract verification failed:\n{e}")

        if e.contract_result:
            # If a contract result is available, it's possible to log it or do something with it
            logging.exception(f"Contract result:\n{e.contract_result}")
