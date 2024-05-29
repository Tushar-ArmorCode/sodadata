from __future__ import annotations

from soda.contracts.contract import Contract, ContractResult
from soda.contracts.impl.data_source import DataSource
from soda.contracts.impl.yaml_helper import YamlFile


class VerificationDataSource:
    """
    Groups all contracts for a specific data_source. Used during contract verification execution to group all
    contracts per data_source and ensure the data_source is open during verification of the contract for this data_source.
    """

    def __init__(self) -> None:
        self.data_source: DataSource | None = None
        self.contracts: list[Contract] = []

    def requires_with_block(self) -> bool:
        return True

    def add_contract(self, contract: Contract) -> None:
        self.contracts.append(contract)

    def ensure_open_and_verify_contracts(self) -> list[ContractResult]:
        """
        Ensures that the data source has an open connection and then invokes self.__verify_contracts()
        """
        if self.requires_with_block():
            with self.data_source as d:
                return self.verify_contracts()
        else:
            return self.verify_contracts()

    def verify_contracts(self):
        """
        Assumes the data source has an open connection
        """
        contract_results: list[ContractResult] = []
        for contract in self.contracts:
            contract_result: ContractResult = contract.verify()
            contract_results.append(contract_result)
        return contract_results


class FileVerificationDataSource(VerificationDataSource):
    def __init__(self, data_source_yaml_file: YamlFile):
        super().__init__()
        self.data_source_file: YamlFile = data_source_yaml_file
        self.data_source = DataSource.from_yaml_file(self.data_source_file)


class SparkVerificationDataSource(VerificationDataSource):
    def __init__(self, spark_session: object, data_source_name: str = "spark_ds"):
        super().__init__()
        self.spark_session: object = spark_session
        self.data_source_name = data_source_name
        self.data_source = DataSource.from_spark_session(spark_session=self.spark_session)
