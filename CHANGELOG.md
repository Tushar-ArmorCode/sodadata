# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [2.1.0b20] - 2021-11-09 *Elrond*

- Core: Fix redshift CI test details
- Core: Fix typo in command help

## [2.1.0b19] - 2021-11-09 *Elrohir*

- Core/Cloud: Add Soda Cloud metrics store support (#528)
- Core: Disable samples and failed row collection based on a setting (#517)
- Core: deprecate to_json and introduce to_dict (#510)
- Core: Add short_help (#546)
- Core: Add github issue link in exception messages (#530)
- BigQuery: Fix auth scope parsing as a list (#524)
- BigQuery: remove unnecessary error during create (#520)
- Snowflake: Add support to set session parameters (#514)

## [2.1.0b18] - 2021-10-05 *Elladan*

- Core: Fix timeout validation
- Spark: Filter columns in spark dialect

## [2.1.0b17] - 2021-09-21 *Denethor II*

- Core: Fix test connection method
- Spark: Add support for pyodbc/databricks
- Spark: Allow spark dialect to work without database specified

## [2.1.0b16] - 2021-09-07 *Celeborn*

- Core: fix time option as it's always set to now by default (#473)
- Core: Update dev requirements
- Core: Update readme with dialect status (#477)
- Core: Update Tox in dev requirements to prevent version deadlock (#474)
- BigQuery: fix NoneType issue when credentials are not sufficient for BigQuery (#472)
- BigQuery: Update bigquery dependency version (#470)
- MySQL: Fix MySQL dialect issues (#475)

## [2.1.0b15] - 2021-09-01 *Barliman Butterbur*

- Core: Implement option to limit the number of tables analyzed (#466)
- Core: Add --offline flag to scan cli to skip sending results to Soda Cloud (#192) (#448)
- Core: Update logging with module names (#447)
- Core: add --non-interactive and --time flag (#455)
- Core: Update unsupported columns message as warning (#460)
- Core/Soda Cloud: Validate warehouse connection method, basic Redshift connection validation (#125) (#454)
- Soda Cloud: truncate columns longer than a length of 200 (#453)
- Soda Cloud: Evaluate test expressions and send them to the cloud to be displayed (#239) (#449)
- BigQuery: Get bigquery account info from reading an external path (#451)

## [2.1.0b14] - 2021-08-18 *Meriadoc Brandybuck*

- Core: Change dependencies to use ranges (#435)
- Core: Adjust logging level with env var (#399) (#442)
- Core: add default encoding to utf8 everywhere (#441)
- Core: Implements sql_test_connection for all warehouses
- Athena: Support for AWS profile based connection (#397)
- Soda Cloud: Send error_code to backend when available (#351) (#443)

## [2.1.0b13] - 2021-08-03 *Boromir*

- Core: Add validation to valid_min, valid_max, and valid_values
- Core: Add support for using variables in tests
- BigQuery: Make AuthScopes configurable
- MySQL: More tests to check the completeness
- Spark: Merge and release first version of Spark dialect

## [2.1.0b12] - 2021-07-23 *Tom Bombadil*

- MySQL: Experimental MySQL Support
- Core: Add excluded_columns feature
- Core: Add limit to custom metrics failed_rows query (#392)
- Core: Updates log level from error to warning for columns with unsupported data types (#391)
- Core: Use the sampler failed_limit for failed rows limit (#394)
- Soda Cloud: Rename validValues -> allowedValues
- Soda Cloud: Rename semanticType to logicalType
- Soda Cloud: Update validity formats
- Soda Cloud: Add SODA_SCAN_ORIGIN env var support (#386)
- Maintenance: Update urllib3
- Maintenance: Pin dependencies to known working versions (#389)
- Maintenance: make the recreate_venv.sh script work again (#381)
- Examples/Docs: Add example AWS lambda function

## [2.1.0b11] - 2021-07-07 *Fredegar Bolger*

### Fixes

- Hive: Add 'authentication' parameter to warehouse config
- Hive: Add string type
- Hive: Implement is_time function
- Soda Cloud: Fix maximumValue monitor type
- Soda Cloud: Prevent memory issues when flushing measurements
- Soda Cloud: Failed rows should add all columns
- Athena/Redshift: Add AWS profile support (Thank you! @Tonkonozhenko)
- Athena: Fix is_number (Thank you! @Tonkonozhenko)
- Docs: Document creating a new dialect (Thank you! @JCZuurmond)

## In-progress:

- SQLServer Quoting issues
- spark-sql dialect (Kudos @JCZuurmond and
  @jchoekstra) https://github.com/sodadata/soda-sql/tree/feature/spark-sql-dialect

## [2.1.0b10] - 2021-06-15 *Bilbo Baggins*

### Fixed

- Soda Cloud: Add origin 'external' to Soda Cloud scan start
- Athena: Add cast to decimal for numeric ops
- Soda Cloud: Send failed rows for custom cloud metrics (aka negative value metrics)
- Github Actions/CI improvements

## [2.1.0b9] - 2021-06-09 *Bergil*

### Fixed

- Athena/Redshift: Fix unwanted precision loss for doubles
- Soda Cloud: Fix failed row count measurements sent to Soda Cloud

## [2.1.0b8] - 2021-06-03 *Beregond*

## Fixed

- core: Skip tests when metrics are null

## [2.1.0b7] - 2021-05-26 *Frodo Baggins*

### Fixed

- Soda Cloud: Add support for custom metrics, filter with different semantic types
- core: Fix unspecified metrics calculation

### In-Progress

- SQLServer test coverage

## [2.1.0b6] - 2021-05-18 *Arwen*

### Fixed

- core: Add is_temporal to identify date/time semantic type
- core: Fix valid_min and valid_max calculation for varchar with numeric data
- soda cloud: Add support for IS NULL sql expression
- snowflake: Privatekey authentication support

## [2.1.0b5] - 2021-05-11 *Aragorn*

### Fixed

- core: enable passing any parameters as environment variables
- core: remove mandatory parsing of env_vars unless env_var function is used
- soda cloud: Add support for custom cloud metrics
- redshift: Update supported datatypes
- snowflake: Don't upcase or quote identifiers
- sqlserver: add trusted_connection parameter for AD/Windows Authentication

## [2.1.0b4] - 2021-05-04

### Fixed

- Logs error message when invalid columns are configured in yml (#297)
- Adds nullable and semantic_type to schema metric (#294)
- Add warehouse dockerfile with pre-populated demodata
- validate scan time ISO 8601 compliance (#285)

## [2.1.0b3] - 2021-04-28

### Fixed

- SQLServer: Fix soda analyze
- SQLServer: Limit (TOP) works in queries
- Metrics: scan command fails when a date validation is added
- Metrics: scan command fails when valid_format is added to
- Snowflake: role and other parameters can be configured in warehouse.yml

## [2.1.0b2] - 2021-04-20

### Fixed

- Fixed metric_groups not calculating all relevant metrics
- Frequent values are calculated for al metric types
- Fix Soda CLI return code
- `soda create bigquery` command doesn't throw error anymore
- Added scopes to Bigquery credentials
- Default scan time is set to UTC

### Changed

- Soda docs are now in a separate [repository](https://github.com/sodadata/docs)

## [2.1.0b1] - 2021-04-08

### Added

- Separated code into different modules, see [RFC](https://github.com/sodadata/soda-sql/discussions/209)

## [2.0.0b27] - 2021-04-08

### Added

- Documentation updates

### Fixed

- Warehouse fixture cleanup

## [2.0.0b26] - 2021-03-31

### Changed

- Update dependencies to their latest versions
- Fix JSON serialization issues with decimals
- Refactor the way how errors are shown during a scan
- Add support for Metric Groups
- Add experimental support for SQL Metrics which produce `failed_rows`
- Add experimental support for dataset sampling (Soda Cloud)

## [2.0.0b25] - 2021-03-17

### Improved

- new parameter `catalog` added in Athena warehouse configuration

### Changed

- Hive support dependencies have been included in the release package

## [2.0.0b24] - 2021-03-16

### Changed

- Athena complex row type fix

## [2.0.0b23] - 2021-03-16

### Changed

- Fixed metadata bug

## [2.0.0b22] - 2021-03-15

### Changed

- Fixed bug in serialization of group values
- Added Hive dialect (Thanks, @ilhamikalkan !)
- In scan, skipping columns with unknown data types
- Improved analyzer should avoid full scan (Thanks, @mmigdiso !)
- Fixed valid_values configuration

## [2.0.0b21] - 2021-03-08

### Changed

- Improved error handling for Postgres/Redshift
- Adaptations in `.editorconfig` to align with PEP-8
- Documentation improvements and additions
- Managed scan support in scan launching flow

## [2.0.0b20] - 2021-03-05

### Changed

- Error handling of failed scans improvements
- Fixed histogram query filter bug. Thanks mmigdiso for the contribution!
- Added build badge to README.md

## [2.0.0b19] - 2021-03-04

###

- `2.0.0b18` was a broken release missing some files. This releases fixes that. It does not introduce any new features.

## [2.0.0b18] - 2021-03-04

### Changed

- Fixed bug in analyze command in BigQuery for STRUCT & ARRAY columns

## [2.0.0b17] - 2021-03-04

### Added

- Added support for Python 3.9 (Big tnx to the Snowflake connector update!)

### Changed

- Switched from yaml FullLoader to SafeLoader as per suggestion of 418sec. Tnx!
- Fixed Decimal jsonnable bug when serializing test results
- Improved logging

## [2.0.0b16] - 2021-03-01

### Changed

- Initial SQLServer dialect implementation (experimental), contributed by Eric. Tnx!
- Scan logging improvements
- Fixed BigQuery connection property docs
- Fixed json Decimal serialization bug when sending test results to Soda cloud
- Fixed validity bug (min/max)

## [2.0.0b15] - 2021-02-24

### Changed

- Add support for role assumption in Athena and Redshift
- Add support for detection of connectivity and authentication issues
- Improvements in cross-dialect quote handling

## [2.0.0b14] - 2021-02-23

### Changed

- Added create connection args / kwargs
- Fixed missing values in the soda scan start request

## [2.0.0b13] - 2021-02-22

### Changed

- Fixed Athena schema property #110 111 : Tnx Lieven!
- Improved Airflow & filtering docs
- Improved mins / maxs for text and time columns

## [2.0.0b12] - 2021-02-16

### Changed

- Renamed CLI command init to analyze!
- (Internal refactoring) Extracted dataset analyzer

## [2.0.0b11] - 2021-02-16

### Changed

- Added missing table metadata queries for athena and bigquery (#97)

## [2.0.0b10] - 2021-02-11

### Changed

- Internal changes (token authorization)

## [2.0.0b9] - 2021-02-10

### Changed

- Internal changes (scan builder, authentication and API changes)

## [2.0.0b8] - 2021-02-08

### Changed

- Fixed init files
- Fixed scan logs

## [2.0.0b7] - 2021-02-06

### Changed

- Moved the SQL metrics inside the scan YAML files, with option to specify the SQL inline or refer to a file.

### Added

- Added column level SQL metrics
- Added documentation on SQL metric variables

## [2.0.0b6] - 2021-02-05

### Changed

- Upgrade library dependencies (dev-requirements.in) to their latest patch
- In scan.yml files, extracted metric categories from `metrics` into a separate `metric_groups` element

## [2.0.0b5] - 2021-02-01

### Changed

- Fixed Snowflake CLI issue

## [2.0.0b4] - 2021-02-01

### Changed

- Packaging issue solved which blocked CLI bootstrapping

## [2.0.0b3] - 2021-01-31

### Added

- Support for Snowflake
- Support for AWS Redshift
- Support for AWS Athena
- Support for GCP BigQuery
- Anonymous tests

### Changed

- Improved [docs on tests](https://docs.soda.io/soda-sql/documentation/tests.html)

## [2.0.0b2] - 2021-01-22

### Added

- Support for AWS PostgreSQL

### Changed

- Published [docs online](https://docs.soda.io/soda-sql/)

## [2.0.0b1] - 2021-01-15

Initial release
