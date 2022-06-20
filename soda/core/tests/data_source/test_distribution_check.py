from textwrap import dedent

import pytest
from tests.helpers.common_test_tables import customers_dist_check_test_table
from tests.helpers.data_source_fixture import DataSourceFixture
from tests.helpers.fixtures import test_data_source


def test_distribution_check(data_source_fixture: DataSourceFixture, mock_file_system):
    table_name = data_source_fixture.ensure_test_table(customers_dist_check_test_table)
    table_name = data_source_fixture.data_source.default_casify_table_name(table_name)

    scan = data_source_fixture.create_test_scan()

    user_home_dir = mock_file_system.user_home_dir()

    mock_file_system.files = {
        f"{user_home_dir}/customers_size_distribution_reference.yml": dedent(
            f"""
            dataset: {table_name}
            column: size
            distribution_type: continuous
            distribution_reference:
                bins: [1, 2, 3]
                weights: [0.5, 0.2, 0.3]
        """
        ).strip(),
    }

    scan.add_sodacl_yaml_str(
        f"""
        checks for {table_name}:
            - distribution_difference(size, my_happy_ml_model_distribution) >= 0.05:
                distribution reference file: {user_home_dir}/customers_size_distribution_reference.yml
                method: ks
    """
    )

    scan.enable_mock_soda_cloud()
    scan.execute()


@pytest.mark.parametrize(
    "table, expectation",
    [
        pytest.param(
            customers_dist_check_test_table, "SELECT \n  size \nFROM {schema_name}{table_name}\n LIMIT 1000000"
        ),
    ],
)
def test_distribution_sql(data_source_fixture: DataSourceFixture, mock_file_system, table, expectation):
    table_name = data_source_fixture.ensure_test_table(table)
    table_name = data_source_fixture.data_source.default_casify_table_name(table_name)

    scan = data_source_fixture.create_test_scan()
    user_home_dir = mock_file_system.user_home_dir()

    mock_file_system.files = {
        f"{user_home_dir}/customers_size_distribution_reference.yml": dedent(
            f"""
            dataset: {table_name}
            column: size
            distribution_type: continuous
            distribution_reference:
                bins: [1, 2, 3]
                weights: [0.5, 0.2, 0.3]
        """
        ).strip(),
    }

    scan.add_sodacl_yaml_str(
        f"""
            checks for {table_name}:
                - distribution_difference(size, my_happy_ml_model_distribution) >= 0.05:
                    distribution reference file:  {user_home_dir}/customers_size_distribution_reference.yml
                    method: ks
        """
    )

    scan.enable_mock_soda_cloud()
    scan.execute()
    if test_data_source != "spark_df":
        assert scan._checks[0].query.sql == expectation.format(
            table_name=table_name, schema_name=f"{data_source_fixture.schema_name}."
        )
    else:
        assert scan._checks[0].query.sql == expectation.format(table_name=table_name, schema_name="")
