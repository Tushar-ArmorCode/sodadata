---
layout: default
title: CLI
parent: Documentation
nav_order: 2
---

# Soda's Command Line Interface (CLI)

> See our [Installation guide]({% link getting-started/installation.md %}) on how to install the `soda` command.

The soda command line tool helps you to get started with
your Soda SQL configuration files and run Soda Scans.

To see the list of available commands, enter `soda` in your terminal:

```
$ soda
Usage: soda [OPTIONS] COMMAND [ARGS]...

  Soda CLI version {version}

Options:
  --help  Show this message and exit.

Commands:
  create  Creates a new warehouse.yml file and prepares credentials in your...
  init    Finds tables in the warehouse and creates scan YAML files based
          on...

  scan    Computes all measurements and runs all tests on one table.
```

| Command | Description |
| ------- | ----------- |
| `soda create ...` | Creates a new `warehouse.yml` file and prepares credentials in your `~/.soda/env_vars.yml`. Nothing will be overwritten or removed, only added if it doesn't exist yet. |
| `soda init ...` | Finds tables in your warehouse and creates scan YAML files for each table. Files are created in a subdirectory called "tables" next to the warehouse file. |
| `soda scan ...` | Computes all measurements and runs all tests on one table.  Exit code 0 means all tests passed. Non zero exit code means tests have failed or an exception occurred. If the warehouse YAML file has a Soda cloud account configured, measurements and test results will be uploaded. |

To learn about the parameters, use the command line help:
* `soda create --help`
* `soda init --help`
* `soda scan --help`

# Env vars

To keep your `warehouse.yml` configuration files free of credentials, soda-sql
supports to reference to environment variables by using the `env_var(SOME_ENV_VAR)` format.

The `soda` CLI uses a convenient mechanism to load environment variables from your local
user home directory.  Each `soda` CLI command which reads a warehouse configuration will
also read the corresponding environment variables specified in your
`~/.soda/env_vars.yml` file.

Example `~/.soda/env_vars.yml`
```yaml
my_project_postgres:
    SNOWFLAKE_USERNAME: someotherexampleusername
    SNOWFLAKE_PASSWORD: someotherexamplepassword

some_other_soda_project:
    POSTGRES_USERNAME: myexampleusername
    POSTGRES_PASSWORD: myexamplepassword
```

The `soda create` command will assist in creating and prepopulating the
environment variables section in your `~/.soda/env_vars.yml` file.