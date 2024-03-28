from __future__ import annotations

import logging
from datetime import date
from textwrap import dedent

from helpers.data_source_fixture import DataSourceFixture
from helpers.test_table import TestTable
from soda.contracts.contract import Contract, ContractResult
from soda.contracts.contract_verification import ContractVerification, ContractVerificationResult
from soda.contracts.data_source import DataSource
from soda.execution.data_type import DataType

contracts_api_test_table = TestTable(
    name="contracts_api",
    columns=[
        ("id", DataType.TEXT),
        ("size", DataType.DECIMAL),
        ("distance", DataType.INTEGER),
        ("created", DataType.DATE),
    ],
    # fmt: off
    values=[
        ('ID1',  1,    0,       date(2020, 6, 23)),
        ('N/A',  1,    None,    date(2020, 6, 23)),
        (None,   1,    None,    date(2020, 6, 23)),
    ]
    # fmt: on
)


def test_contract_api(data_source_fixture: DataSourceFixture, environ: dict):
    table_name: str = data_source_fixture.ensure_test_table(contracts_api_test_table)

    data_source_yaml_str = dedent(
        """
        name: postgres_ds
        type: postgres
        connection:
            host: localhost
            database: sodasql
            username: sodasql
    """
    )

    contract_yaml_str = dedent(
        f"""
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
    """
    )

    contract_verification_result: ContractVerificationResult = (
        ContractVerification()
        .with_contract_yaml_str(contract_yaml_str)
        .with_data_source_yaml_str(data_source_yaml_str)
        .with_variables({})
        .execute()
    )
    logging.debug(str(contract_verification_result))


    # Example that picks up the data source from user home
    contract_result: ContractResult = (
        Contract
        .from_yaml_str(contract_yaml_str)
        .with_data_source_from_user_home()
        .verify()
    )

    # Example that picks up the data source from relative files
    contract_result: ContractResult = (
        Contract
        .from_yaml_file(contract_yaml_file_path="./customers.contract.yml")
        .with_data_source_from_parent_folders()
        .verify()
    )

    # Running multiple contracts on the same connection?
    file_path = "./postgres.datasource.yml"
    with DataSource.from_yaml_file(file_path) as data_source:
        contract_result: ContractResult = (
            Contract
            .from_yaml_file(contract_yaml_file_path="./customers.contract.yml")
            .with_data_source_from_parent_folders()
            .verify()
        )
        contract_result: ContractResult = (
            Contract
            .from_yaml_file(contract_yaml_file_path="./suppliers.contract.yml")
            .with_data_source_from_parent_folders()
            .verify()
        )

    # try:
    #     # Optionally a Soda Cloud link can be established that
    #     #  - Enables change-over-time thresholds in checks using the Soda Cloud metric store
    #     #  - Collects and displays all contract results and diagnostics information
    #     #  - Central place from which people can subscribe and notifications get dispatched
    #
    #     # Using a SodaCloud instance will send the results to Cloud and make this test run over 2 seconds
    #     soda_cloud: SodaCloud | None = None  # SodaCloud.from_environment_variables()
    #
    #     # The connection to the SQL-engine
    #     with Connection.from_yaml_str(connection_yaml_str) as connection:
    #
    #         # Parsing the contract YAML into a contract python object
    #         contract: Contract = Contract.from_yaml_str(contract_yaml_str)
    #
    #         contract_result: ContractResult = contract.verify(connection, soda_cloud)
    #
    #         # This place in the code means contract verification has passed successfully:
    #         # No exceptions means there are no contract execution exceptions and no check failures.
    #
    #         # The default way to visualize diagnostics information for checks is Soda Cloud.
    #         # But contract results information can be transformed and sent to any destination
    #         # (contract_results includes information like eg the check results and diagnostics information)
    #         logging.debug(f"Contract verification passed:\n{contract_result}")
    #
    # except SodaException as e:
    #     # An exception is raised means there are either check failures or contract verification exceptions.
    #     # Those include:
    #     # -
    #     logging.exception(f"Contract verification failed:\n{e}", exc_info=e)


# def test_connection_exception_is_raised_in_contract_verify(data_source_fixture: DataSourceFixture):
#     table_name: str = data_source_fixture.ensure_test_table(contracts_test_table)
#
#     contract_yaml_str = dedent(
#         f"""
#       dataset: {table_name}
#       columns:
#       - name: id
#       - name: size
#       - name: distance
#       - name: created
#     """
#     )
#
#     with Connection.from_yaml_file("./non_existing_file.scn.yml") as connection:
#         contract: Contract = Contract.from_yaml_str(contract_yaml_str)
#         with pytest.raises(SodaException) as excinfo:
#             contract.verify(connection)
#     exception = excinfo.value
#     assert isinstance(exception, SodaException)
#     assert "file './non_existing_file.scn.yml'" in str(exception)
#     assert "No such file or directory" in str(exception)
