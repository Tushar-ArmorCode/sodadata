from __future__ import annotations

import dataclasses
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from numbers import Number
from typing import Dict

from soda.contracts.impl.logs import Logs
from soda.contracts.impl.yaml_helper import YamlHelper
from soda.scan import Scan

logger = logging.getLogger(__name__)


class Check(ABC):

    def __init__(
            self,
            logs: Logs,
            verification_context: str,
            type: str,
            check_yaml: dict
    ):
        self.logs: Logs = logs
        self.verification_context: str = verification_context
        self.type: str = type
        self.check_yaml: dict = check_yaml
        self.identity: str = self._create_identity()
        self.skip: bool = False

    @abstractmethod
    def to_sodacl_check(self) -> str | dict | None:
        pass

    @abstractmethod
    def create_check_result(
        self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan
    ) -> CheckResult:
        pass

    def _create_identity(self) -> str:
        return f"{self.verification_context},type={self.type}"


class CheckResult:

    def __init__(self,
                 check: Check,
                 outcome: CheckOutcome
                 ):
        self.check: Check = check
        self.outcome: CheckOutcome = outcome

    def __str__(self) -> str:
        return "\n".join(self.get_contract_result_str_lines())

    @abstractmethod
    def get_contract_result_str_lines(self) -> list[str]:
        """
        Provides the summary for the contract result logs, as well as the __str__ impl of this check result.
        Method implementations can use self._get_outcome_line(self)
        """

    def get_outcome_and_name_line(self) -> str:
        name_str: str = f" [{self.check.name}]" if self.check.name else ""
        return f"Check {self.get_outcome_str()}{name_str}"

    def get_outcome_str(self) -> str:
        if self.outcome == CheckOutcome.FAIL:
            return "FAILED"
        if self.outcome == CheckOutcome.PASS:
            return "passed"
        return "unverified"


class SchemaCheck(Check):

    def __init__(self, logs: Logs, verification_context: str, yaml_contract: dict):
        super().__init__(
            logs=logs,
            verification_context=verification_context,
            type="schema",
            check_yaml=yaml_contract
        )

        self.columns: dict[str, str] = {}
        self.optional_columns: list[str] = []

        yaml_helper = YamlHelper(logs=self.logs)
        extra_columns: str | None = yaml_helper.read_string_opt(yaml_contract, "extra_columns")
        self.extra_columns_allowed: bool = "allowed" == extra_columns

        yaml_columns: list | None = yaml_helper.read_yaml_list(yaml_contract, "columns")
        if yaml_columns:
            for yaml_column in yaml_columns:
                column_name: str | None = yaml_helper.read_string(yaml_column, "name")
                data_type: str | None = yaml_helper.read_string_opt(yaml_column, "data_type")
                if column_name:
                    self.columns[column_name] = data_type

                is_column_optional = yaml_helper.read_bool_opt(yaml_column, "optional", default_value=False)
                if is_column_optional:
                    self.optional_columns.append(column_name)


    def to_sodacl_check(self) -> str | dict | None:
        schema_fail_dict = {"when mismatching columns": self.columns}
        if self.optional_columns:
            schema_fail_dict["with optional columns"] = self.optional_columns
        return {"schema": {"fail": schema_fail_dict}}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan):
        scan_measured_schema: list[dict] = scan_check_metrics_by_name.get("schema").get("value")
        measured_schema = {c.get("columnName"): c.get("sourceDataType") for c in scan_measured_schema}

        diagnostics = scan_check.get("diagnostics", {})

        columns_not_allowed_and_present: list[str] = diagnostics.get("present_column_names", [])
        columns_required_and_not_present: list[str] = diagnostics.get("missing_column_names", [])

        columns_having_wrong_type: list[DataTypeMismatch] = []
        scan_column_type_mismatches = diagnostics.get("column_type_mismatches", {})
        if scan_column_type_mismatches:
            for column_name, column_type_mismatch in scan_column_type_mismatches.items():
                expected_type = column_type_mismatch.get("expected_type")
                actual_type = column_type_mismatch.get("actual_type")
                columns_having_wrong_type.append(
                    DataTypeMismatch(column=column_name, expected_data_type=expected_type, actual_data_type=actual_type)
                )

        return SchemaCheckResult(
            check=self,
            outcome=CheckOutcome.from_scan_check(scan_check),
            measured_schema=measured_schema,
            columns_not_allowed_and_present=columns_not_allowed_and_present,
            columns_required_and_not_present=columns_required_and_not_present,
            columns_having_wrong_type=columns_having_wrong_type,
        )


class SchemaCheckResult(CheckResult):

    def __init__(self,
                 check: Check,
                 outcome: CheckOutcome,
                 measured_schema: Dict[str, str],
                 columns_not_allowed_and_present: list[str] | None,
                 columns_required_and_not_present: list[str] | None,
                 columns_having_wrong_type: list[DataTypeMismatch] | None
                 ):
        super().__init__(check, outcome)
        self.measured_schema: Dict[str, str] = measured_schema
        self.columns_not_allowed_and_present: list[str] | None = columns_not_allowed_and_present
        self.columns_required_and_not_present: list[str] | None = columns_required_and_not_present
        self.columns_having_wrong_type: list[DataTypeMismatch] | None = columns_having_wrong_type

    def get_contract_result_str_lines(self) -> list[str]:
        schema_check: SchemaCheck = self.check
        expected_schema: str = ",".join(
            [
                f"{c.get('name')}{c.get('optional')}{c.get('type')}"
                for c in [
                    {
                        "name": column_name,
                        "optional": "(optional)" if column_name in schema_check.optional_columns else "",
                        "type": f"={data_type}" if data_type else "",
                    }
                    for column_name, data_type in schema_check.columns.items()
                ]
            ]
        )

        lines: list[str] = [
            f"Schema check {self.get_outcome_str()}",
            f"  Expected schema: {expected_schema}",
            f"  Actual schema: {self.measured_schema}",
        ]
        lines.extend(
            [f"  Column '{column}' was present and not allowed" for column in self.columns_not_allowed_and_present]
        )
        lines.extend([f"  Column '{column}' was missing" for column in self.columns_required_and_not_present])
        lines.extend(
            [
                (
                    f"  Column '{data_type_mismatch.column}': Expected type '{data_type_mismatch.expected_data_type}', "
                    f"but was '{data_type_mismatch.actual_data_type}'"
                )
                for data_type_mismatch in self.columns_having_wrong_type
            ]
        )
        return lines


class CheckFactory(ABC):
    @abstractmethod
    def create_check(self, **kwargs) -> Check | None:
        pass


class AbstractCheck(Check, ABC):

    threshold_keys = [
        "must_be_greater_than",
        "must_be_greater_than_or_equal_to",
        "must_be_less_than",
        "must_be_less_than_or_equal_to",
        "must_be",
        "must_not_be",
        "must_be_between",
        "must_be_not_between",
    ]

    validity_keys = [
        "invalid_values",
        "invalid_format",
        "invalid_sql_regex",
        "valid_values",
        "valid_format",
        "valid_sql_regex",
        "valid_min",
        "valid_max",
        "valid_length",
        "valid_min_length",
        "valid_max_length",
        "valid_values_reference_data",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: str | None = kwargs["check_name"]
        # column can be unspecified in the kwargs in case of dataset level checks,
        # hence the kwargs.get("column") instead of kwargs["column"]
        self.column: str | None = kwargs.get("column")
        self.missing_configurations: MissingConfigurations = kwargs["missing_configurations"]
        self.valid_configurations: ValidConfigurations = kwargs["valid_configurations"]
        self.threshold: NumericThreshold = kwargs["threshold"]

    def _create_identity(self) -> str:
        yaml_helper = YamlHelper(self.logs)

        # TODO check the identity suffix with a regex so it is all lower case, numbers and underscores no spaces.
        #      Either here or better yet in the json schema, but then make sure it's in the errors

        identity = f"{self.verification_context},type={self.type}"

        # Check identifier used to correlate the sodacl check results with this contract check object when parsing
        # scan results.  Also used as correlation id in Soda Cloud to match subsequent results for the same check.
        # Composite key created from schedule, dataset, column, type and identity_suffix.
        identity_suffix = yaml_helper.read_string_opt(self.check_yaml, "identity_suffix")
        if identity_suffix:
            identity += f",identity_suffix={identity_suffix}"

        return identity


class MissingCheckFactory(CheckFactory):
    def create_check(self, **kwargs) -> Check | None:
        check_type = kwargs["check_type"]
        if check_type in ["no_missing_values", "missing_count", "missing_percent"]:
            metric = "missing_count" if check_type == "no_missing_values" else check_type
            return MetricCheck(metric=metric, **kwargs)


class InvalidCheckFactory(CheckFactory):
    def create_check(self, **kwargs) -> Check | None:
        check_type = kwargs["check_type"]
        if check_type in ["no_invalid_values", "invalid_count", "invalid_percent"]:
            valid_configurations: ValidConfigurations = kwargs["valid_configurations"]
            if valid_configurations and valid_configurations.valid_values_reference_data:
                return ReferenceDataCheck(**kwargs)
            else:
                metric = "invalid_count" if check_type == "no_invalid_values" else check_type
                return MetricCheck(metric=metric, **kwargs)


class DuplicateCheckFactory(CheckFactory):
    def create_check(self, **kwargs) -> Check | None:
        check_type = kwargs["check_type"]
        if check_type in ["no_duplicate_values", "duplicate_count", "duplicate_percent"]:
            metric = "duplicate_count" if check_type == "no_duplicate_values" else check_type
            return MetricCheck(metric=metric, **kwargs)


class SqlFunctionCheckFactory(CheckFactory):
    def create_check(self, **kwargs) -> Check | None:
        check_type = kwargs["check_type"]
        return MetricCheck(metric=check_type, **kwargs)


class MetricCheck(AbstractCheck):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metric: str = kwargs["metric"]

    def to_sodacl_check(self) -> str | dict | None:
        sodacl_check_line = self.get_sodacl_check_line()

        sodacl_check_configs = {"contract check id": self.identity}

        if self.name:
            sodacl_check_configs["name"] = self.name

        if self.valid_configurations:
            sodacl_check_configs.update(self.valid_configurations.to_sodacl_check_configs_dict())
        if self.missing_configurations:
            sodacl_check_configs.update(self.missing_configurations.to_sodacl_check_configs_dict())

        return {sodacl_check_line: sodacl_check_configs}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan):
        scan_metric_dict: dict
        if "(" in self.metric:
            scan_metric_name = self.metric[: self.metric.index("(")]
            scan_metric_dict = scan_check_metrics_by_name.get(scan_metric_name, None)
        else:
            scan_metric_dict = scan_check_metrics_by_name.get(self.metric, None)
        metric_value: Number = scan_metric_dict.get("value") if scan_metric_dict else None
        return MetricCheckResult(
            check=self, outcome=CheckOutcome.from_scan_check(scan_check), metric_value=metric_value
        )

    def get_sodacl_check_line(self) -> str:
        sodacl_metric = self.get_sodacl_metric()
        sodacl_threshold: str = self.threshold.get_sodacl_threshold() if self.threshold else ""
        return f"{sodacl_metric} {sodacl_threshold}"

    def get_sodacl_metric(self) -> str:
        return f"{self.metric}({self.column})" if self.column else self.metric

    def get_sodacl_threshold(self) -> str:
        return self.threshold.get_sodacl_threshold() if self.threshold else "?"

    def get_metric_str(self) -> str:
        return self.get_sodacl_metric()

    def get_expected_str(self) -> str:
        return f"{self.get_metric_str()} {self.get_sodacl_threshold()}"


class MetricCheckResult(CheckResult):
    def __init__(self,
                 check: Check,
                 outcome: CheckOutcome,
                 metric_value: Number,
                 ):
        super().__init__(check, outcome)
        self.metric_value: Number = metric_value

    def get_contract_result_str_lines(self) -> list[str]:
        return [
            self.get_outcome_and_name_line(),
            f"  Expected {self.check.get_expected_str()}",
            f"  Actual {self.check.get_metric_str() } was {self.metric_value}",
        ]


class ReferenceDataCheck(MetricCheck):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.valid_values_reference_data: ValidValuesReferenceData = kwargs["valid_values_reference_data"]

    def to_sodacl_check(self) -> str | dict | None:
        sodacl_check_configs = {"contract check id": self.identity}

        if self.name:
            sodacl_check_configs["name"] = self.name

        if self.valid_configurations:
            sodacl_check_configs.update(self.valid_configurations.to_sodacl_check_configs_dict())
        if self.missing_configurations:
            sodacl_check_configs.update(self.missing_configurations.to_sodacl_check_configs_dict())

        sodacl_check_line: str = (
            f"values in ({self.column}) must exist in {self.valid_values_reference_data.dataset} ({self.valid_values_reference_data.column})"
        )

        return {sodacl_check_line: sodacl_check_configs}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan):
        scan_metric_dict = scan_check_metrics_by_name.get("reference", {})
        value: Number = scan_metric_dict.get("value")
        return MetricCheckResult(
            check=self, outcome=CheckOutcome.from_scan_check(scan_check), metric_value=value
        )


class UserDefinedMetricExpressionSqlCheckFactory(CheckFactory):
    def create_check(self, **kwargs) -> Check | None:
        check_type: str = kwargs["check_type"]
        if check_type == "metric_expression_sql":
            return UserDefinedMetricExpressionSqlCheck(**kwargs)


class UserDefinedMetricExpressionSqlCheck(MetricCheck):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        yaml_source: dict = kwargs["yaml_source"]
        self.metric_expression_sql: str = kwargs.get("metric_expression_sql")

    def to_sodacl_check(self) -> str | dict | None:
        sodacl_check_configs = {
            "contract check id": self.identity,
            f"{self.metric} expression": self.metric_expression_sql,
        }
        if self.name:
            sodacl_check_configs["name"] = self.name

        sodacl_checkline_threshold = self.threshold.get_sodacl_threshold()
        sodacl_check_line = f"{self.get_sodacl_metric()} {sodacl_checkline_threshold}"

        return {sodacl_check_line: sodacl_check_configs}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict],
                            scan: Scan):
        scan_metric_dict: dict = scan_check_metrics_by_name.get(self.metric, None)
        metric_value: Number = scan_metric_dict.get("value") if scan_metric_dict else None
        return MetricCheckResult(
            check=self, outcome=CheckOutcome.from_scan_check(scan_check), metric_value=metric_value
        )


class FreshnessCheck(AbstractCheck):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_definition_line(self) -> str:
        return f"freshness({self.column}) {self.threshold.get_sodacl_threshold()}{self.get_sodacl_time_unit()}"

    def get_sodacl_time_unit(self) -> str:
        sodacl_time_unit_by_check_type = {
            "freshness_in_days": "d",
            "freshness_in_hours": "h",
            "freshness_in_minutes": "m",
        }
        return sodacl_time_unit_by_check_type.get(self.type)

    def to_sodacl_check(self) -> str | dict | None:
        sodacl_check_configs = {
            "contract check id": self.identity,
        }
        if self.name:
            sodacl_check_configs["name"] = self.name

        sodacl_check_line: str = self.get_definition_line()
        return {sodacl_check_line: sodacl_check_configs}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan):
        diagnostics: dict = scan_check["diagnostics"]
        freshness = diagnostics["freshness"]
        freshness_column_max_value = diagnostics["maxColumnTimestamp"]
        freshness_column_max_value_utc = diagnostics["maxColumnTimestampUtc"]
        now = diagnostics["nowTimestamp"]
        now_utc = diagnostics["nowTimestampUtc"]

        return FreshnessCheckResult(
            check=self,
            outcome=CheckOutcome.from_scan_check(scan_check),
            freshness=freshness,
            freshness_column_max_value=freshness_column_max_value,
            freshness_column_max_value_utc=freshness_column_max_value_utc,
            now=now,
            now_utc=now_utc,
        )


@dataclass
class FreshnessCheckResult(CheckResult):
    freshness: str
    freshness_column_max_value: str
    freshness_column_max_value_utc: str
    now: str
    now_utc: str

    def get_contract_result_str_lines(self) -> list[str]:
        assert isinstance(self.check, FreshnessCheck)
        return [
            self.get_outcome_and_name_line(),
            f"  Expected {self.check.get_definition_line()}",
            f"  Actual freshness({self.check.column}) was {self.freshness}",
            f"  Max value in column was ...... {self.freshness_column_max_value}",
            f"  Max value in column in UTC was {self.freshness_column_max_value_utc}",
            f"  Now was ...................... {self.now}",
            f"  Now in UTC was ............... {self.now_utc}",
        ]



@dataclass
class MultiColumnDuplicateCheck(MetricCheck):
    columns: list[str]

    def get_sodacl_metric(self) -> str:
        column_str = self.column if self.column else ", ".join(self.columns)
        return f"{self.metric}({column_str})"





@dataclass
class UserDefinedMetricSqlQueryCheck(MetricCheck):

    metric_sql_query: str

    def to_sodacl_check(self) -> str | dict | None:
        sodacl_check_configs = {
            "contract check id": self.identity,
            f"{self.metric} query": self.metric_sql_query,
        }
        if self.name:
            sodacl_check_configs["name"] = self.name

        sodacl_check_line: str = self.get_sodacl_check_line()

        return {sodacl_check_line: sodacl_check_configs}

    def create_check_result(self, scan_check: dict[str, dict], scan_check_metrics_by_name: dict[str, dict], scan: Scan):
        scan_metric_dict: dict = scan_check_metrics_by_name.get(self.get_sodacl_check_line(), None)
        metric_value: Number = scan_metric_dict.get("value") if scan_metric_dict else None

        return MetricCheckResult(
            check=self, outcome=CheckOutcome.from_scan_check(scan_check), metric_value=metric_value
        )


class CheckOutcome(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"

    @classmethod
    def from_scan_check(cls, scan_check: Dict[str, object]) -> CheckOutcome:
        scan_check_outcome = scan_check.get("outcome")
        if scan_check_outcome == "pass":
            return CheckOutcome.PASS
        elif scan_check_outcome == "fail":
            return CheckOutcome.FAIL
        return CheckOutcome.UNKNOWN


@dataclass
class DataTypeMismatch:
    column: str
    expected_data_type: str
    actual_data_type: str


def dataclass_object_to_sodacl_dict(dataclass_object: object) -> dict:
    def translate_to_sodacl_key(key: str) -> str:
        if "sql_" in key:
            key = key.replace("sql_", "")
        return key.replace("_", " ")

    dict_factory = lambda x: {translate_to_sodacl_key(k): v for (k, v) in x if v is not None}
    return dataclasses.asdict(dataclass_object, dict_factory=dict_factory)


@dataclass
class MissingConfigurations:
    missing_values: list[str] | list[Number] | None
    missing_regex_sql: str | None

    def to_sodacl_check_configs_dict(self) -> dict:
        return dataclass_object_to_sodacl_dict(self)


@dataclass
class ValidConfigurations:
    invalid_values: list[str] | list[Number] | None
    invalid_format: str | None
    invalid_sql_regex: str | None
    valid_values: list[str] | list[Number] | None
    valid_format: str | None
    valid_sql_regex: str | None
    valid_min: Number | None
    valid_max: Number | None
    valid_length: int | None
    valid_min_length: int | None
    valid_max_length: int | None
    valid_values_reference_data: ValidValuesReferenceData | None

    def to_sodacl_check_configs_dict(self) -> dict:
        sodacl_check_configs_dict = dataclass_object_to_sodacl_dict(self)
        sodacl_check_configs_dict.pop("valid values reference data", None)
        return sodacl_check_configs_dict

    def has_non_reference_data_configs(self) -> bool:
        return (
            self.invalid_values is not None
            or self.invalid_format is not None
            or self.invalid_sql_regex is not None
            or self.valid_values is not None
            or self.valid_format is not None
            or self.valid_sql_regex is not None
            or self.valid_min is not None
            or self.valid_max is not None
            or self.valid_length is not None
            or self.valid_min_length is not None
            or self.valid_max_length is not None
        )


@dataclass
class ValidValuesReferenceData:
    dataset: str
    column: str


@dataclass
class NumericThreshold:
    """
    The threshold is exceeded when any of the member field conditions is True.
    To be interpreted as a check fails when the metric value is ...greater_than or ...less_than etc...
    """

    greater_than: Number | None = None
    greater_than_or_equal: Number | None = None
    less_than: Number | None = None
    less_than_or_equal: Number | None = None
    equal: Number | None = None
    not_equal: Number | None = None
    between: Range | None = None
    not_between: Range | None = None

    def get_sodacl_threshold(self) -> str:
        greater_bound: Number | None = (
            self.greater_than if self.greater_than is not None else self.greater_than_or_equal
        )
        less_bound: Number | None = self.less_than if self.less_than is not None else self.less_than_or_equal
        if greater_bound is not None and less_bound is not None:
            if greater_bound > less_bound:
                return self.sodacl_threshold(
                    is_not_between=True,
                    lower_bound=less_bound,
                    lower_bound_included=self.less_than is not None,
                    upper_bound=greater_bound,
                    upper_bound_included=self.greater_than is not None,
                )
            else:
                return self.sodacl_threshold(
                    is_not_between=False,
                    lower_bound=greater_bound,
                    lower_bound_included=self.greater_than_or_equal is not None,
                    upper_bound=less_bound,
                    upper_bound_included=self.less_than_or_equal is not None,
                )
        elif isinstance(self.between, Range):
            return self.sodacl_threshold(
                is_not_between=False,
                lower_bound=self.between.lower_bound,
                lower_bound_included=True,
                upper_bound=self.between.upper_bound,
                upper_bound_included=True,
            )
        elif isinstance(self.not_between, Range):
            return self.sodacl_threshold(
                is_not_between=True,
                lower_bound=self.not_between.lower_bound,
                lower_bound_included=True,
                upper_bound=self.not_between.upper_bound,
                upper_bound_included=True,
            )
        elif self.greater_than is not None:
            return f"> {self.greater_than}"
        elif self.greater_than_or_equal is not None:
            return f">= {self.greater_than_or_equal}"
        elif self.less_than is not None:
            return f"< {self.less_than}"
        elif self.less_than_or_equal is not None:
            return f"<= {self.less_than_or_equal}"
        elif self.equal is not None:
            return f"= {self.equal}"
        elif self.not_equal is not None:
            return f"!= {self.not_equal}"

    @classmethod
    def sodacl_threshold(
        cls,
        is_not_between: bool,
        lower_bound: Number,
        lower_bound_included: bool,
        upper_bound: Number,
        upper_bound_included: bool,
    ) -> str:
        optional_not = "not " if is_not_between else ""
        lower_bound_bracket = "" if lower_bound_included else "("
        upper_bound_bracket = "" if upper_bound_included else ")"
        return f"{optional_not}between {lower_bound_bracket}{lower_bound} and {upper_bound}{upper_bound_bracket}"

    def is_empty(self) -> bool:
        return (
            self.greater_than is None
            and self.greater_than_or_equal is None
            and self.less_than is None
            and self.less_than_or_equal is None
            and self.equal is None
            and self.not_equal is None
            and self.between is None
            and self.not_between is None
        )


@dataclass
class Range:
    """
    Boundary values are inclusive
    """

    lower_bound: Number | None
    upper_bound: Number | None
