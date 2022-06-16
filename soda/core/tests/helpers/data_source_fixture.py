from __future__ import annotations

import logging
import os
import re
import textwrap
from importlib import import_module

from soda.common.lazy import Lazy
from soda.common.yaml_helper import YamlHelper
from soda.scan import Scan
from tests.helpers.test_scan import TestScan
from tests.helpers.test_column import TestColumn
from tests.helpers.test_table import TestTable

logger = logging.getLogger(__name__)


class DataSourceFixture:
    """
    Public methods are to be used in tests.
    Protected methods starting with an underscore (_) are part of the
    test infrastructure and are not to be used in tests.

    """

    __test__ = False

    @staticmethod
    def _create() -> DataSourceFixture:
        test_data_source = os.getenv("test_data_source", "postgres")

        module = import_module(f"tests.{test_data_source}_data_source_fixture")

        if "bigquery" == test_data_source:
            data_source_fixture_class = "BigQueryDataSourceFixture"
        elif "spark_df" == test_data_source:
            data_source_fixture_class = "SparkDfDataSourceFixture"
        else:
            data_source_fixture_class = f"{test_data_source[0:1].upper()}{test_data_source[1:]}DataSourceFixture"

        class_ = getattr(module, data_source_fixture_class)
        return class_(test_data_source)

    def __init__(self, test_data_source: str):
        self.data_source_name = test_data_source
        self.__existing_table_names = Lazy()
        self.schema_name: str = self._create_schema_name()
        self.schema_data_source = None
        self.data_source = None

    def _build_configuration_dict(self, schema_name: str | None = None) -> dict:
        raise NotImplementedError("Override and implement this method")

    def _create_schema_name(self):
        schema_name_parts = []
        github_head_ref = os.getenv("GITHUB_HEAD_REF")
        if github_head_ref:
            schema_name_parts.append("ci")
            schema_name_parts.append(github_head_ref)
            python_version = os.getenv("PYTHON_VERSION")
            python_version = python_version.replace(".", "")
            schema_name_parts.append(python_version)

        else:
            schema_name_parts.append("dev")
            schema_name_parts.append(os.getenv("USER", "anonymous"))
        schema_name_raw = "_".join(schema_name_parts)
        schema_name = re.sub("[^0-9a-zA-Z]+", "_", schema_name_raw)
        return schema_name

    def _test_session_starts(self):
        self.schema_data_source = self._create_schema_data_source()
        self._drop_schema_if_exists()
        self._create_schema_if_not_exists()
        self.data_source = self._create_test_data_source()

    def _create_schema_data_source(self) -> 'DataSource':
        configuration_dict = self._build_configuration_dict()
        configuration_yaml_str = YamlHelper.to_yaml(configuration_dict)
        return self._create_data_source_from_configuration_yaml_str(configuration_yaml_str)

    def _create_data_source_from_configuration_yaml_str(self, configuration_yaml_str: str) -> 'DataSource':
        scan = Scan()
        scan.set_data_source_name(self.data_source_name)
        scan.add_configuration_yaml_str(configuration_yaml_str)
        data_source_manager = scan._data_source_manager
        data_source = data_source_manager.get_data_source(self.data_source_name)
        if not data_source:
            raise Exception(f"Unable to create test data source '{self.data_source_name}'")
        scan._get_or_create_data_source_scan(self.data_source_name)
        return data_source

    def _create_schema_if_not_exists(self):
        create_schema_if_not_exists_sql = self._create_schema_if_not_exists_sql()
        self._update(create_schema_if_not_exists_sql, self.schema_data_source.connection)

    def _create_schema_if_not_exists_sql(self) -> str:
        return f"CREATE DATABASE {self.schema_name}"

    def _create_test_data_source(self) -> 'DataSource':
        configuration_yaml_str = self.create_test_configuration_yaml_str()
        return self._create_data_source_from_configuration_yaml_str(configuration_yaml_str)

    def create_test_configuration_yaml_str(self):
        configuration_dict = self._build_configuration_dict(self.schema_name)
        configuration_yaml_str = YamlHelper.to_yaml(configuration_dict)
        return configuration_yaml_str

    def ensure_test_table(self, test_table: TestTable) -> str:
        """
        Returns a unique test table name with the given table data
        """
        existing_test_table_names = self._get_existing_test_table_names()
        existing_test_table_names_lower = [table_name.lower() for table_name in existing_test_table_names]
        if test_table.unique_table_name.lower() not in existing_test_table_names_lower:
            obsolete_table_names = [
                existing_test_table
                for existing_test_table in existing_test_table_names
                if existing_test_table.lower().startswith(f"sodatest_{test_table.name.lower()}_")
            ]
            if obsolete_table_names:
                for obsolete_table_name in obsolete_table_names:
                    self._drop_test_table(obsolete_table_name)
            self._create_and_insert_test_table(test_table)
            self.data_source.commit()

            # TODO investigate if this is really needed
            self.data_source.analyze_table(test_table.unique_table_name)

        return test_table.unique_table_name

    def _get_existing_test_table_names(self):
        if not self.__existing_table_names.is_set():
            sql = self.data_source.sql_find_table_names(filter="sodatest_%")
            rows = self._fetch_all(sql)
            table_names = [row[0] for row in rows]
            self.__existing_table_names.set(table_names)
        return self.__existing_table_names.get()

    def _create_and_insert_test_table(self, test_table):
        create_table_sql = self._create_test_table_sql(test_table)
        self._update(create_table_sql)
        self._get_existing_test_table_names().append(test_table.unique_table_name)
        insert_table_sql = self._insert_test_table_sql(test_table)
        if insert_table_sql:
            self._update(insert_table_sql)

    def _create_test_table_sql(self, test_table: TestTable) -> str:
        table_name = test_table.unique_table_name
        if test_table.quote_names:
            table_name = self.data_source.quote_table_declaration(table_name)
        qualified_table_name = self.data_source.qualified_table_name(table_name)
        test_columns = test_table.test_columns
        if test_table.quote_names:
            test_columns = [
                TestColumn(
                    name=self.data_source.quote_column_declaration(test_column.name), data_type=test_column.data_type
                )
                for test_column in test_columns
            ]
        columns_sql = ",\n".join(
            [
                f"  {test_column.name} {self.data_source.get_sql_type_for_create_table(test_column.data_type)}"
                for test_column in test_columns
            ]
        )
        return self._create_test_table_sql_compose(qualified_table_name, columns_sql)

    def _create_test_table_sql_compose(self, qualified_table_name, columns_sql) -> str:
        return f"CREATE TABLE {qualified_table_name} ( \n{columns_sql} \n)"

    def _insert_test_table_sql(self, test_table: TestTable) -> str:
        if test_table.values:
            quoted_table_name = (
                self.data_source.quote_table(test_table.unique_table_name)
                if test_table.quote_names
                else test_table.unique_table_name
            )
            qualified_table_name = self.data_source.qualified_table_name(quoted_table_name)

            def sql_test_table_row(row):
                return ",".join(self.data_source.literal(value) for value in row)

            rows_sql = ",\n".join([f"  ({sql_test_table_row(row)})" for row in test_table.values])
            return f"INSERT INTO {qualified_table_name} VALUES \n" f"{rows_sql};"

    def create_test_scan(self) -> TestScan:
        return TestScan(data_source=self.data_source)

    def _test_session_ends(self):
        self.data_source.connection.close()
        self._drop_schema_if_exists()
        self.schema_data_source.connection.close()

    def _drop_schema_if_exists(self):
        drop_schema_if_exists_sql = self._drop_schema_if_exists_sql()
        self._update(drop_schema_if_exists_sql, self.schema_data_source.connection)

    def _drop_schema_if_exists_sql(self) -> str:
        return f"DROP DATABASE {self.schema_name}"

    def _drop_test_table(self, table_name):
        drop_test_table_sql = self._drop_test_table_sql(table_name)
        self._update(drop_test_table_sql)
        self._get_existing_test_table_names().remove(table_name)

    def _drop_test_table_sql(self, table_name):
        qualified_table_name = self.data_source.qualified_table_name(table_name)
        return f"DROP TABLE {qualified_table_name} IF EXISTS;"

    def _fetch_all(self, sql: str, connection=None) -> list[tuple]:
        if connection is None:
            connection = self.data_source.connection
        cursor = connection.cursor()
        try:
            sql_indented = textwrap.indent(text=sql, prefix="  #   ")
            logger.debug(f"  # Test data handler fetchall: \n{sql_indented}")
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()

    def _update(self, sql: str, connection=None) -> object:
        if connection is None:
            connection = self.data_source.connection
        cursor = connection.cursor()
        try:
            sql_indented = textwrap.indent(text=sql, prefix="  #   ")
            logger.debug(f"  # Test data handler update: \n{sql_indented}")
            updates = cursor.execute(sql)
            connection.commit()
            return updates
        finally:
            cursor.close()
