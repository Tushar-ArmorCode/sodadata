"""dbt integeration"""

from __future__ import annotations

from collections import defaultdict
from functools import reduce
from operator import or_
from typing import Any, Optional

from dbt.contracts.graph.compiled import (
    CompiledModelNode,
    CompiledGenericTestNode,
    CompiledSeedNode,
)
from dbt.contracts.graph.parsed import (
    ParsedModelNode,
    ParsedGenericTestNode,
    ParsedSeedNode,
    ParsedSourceDefinition,
)
from dbt.contracts.results import RunResultOutput
from dbt.node_types import NodeType


def parse_manifest(
    manifest: dict[str, Any]
) -> tuple[
        Optional[dict[str, ParsedModelNode | CompiledModelNode]],
        Optional[dict[str, ParsedSeedNode | CompiledSeedNode]],
        Optional[dict[str, ParsedGenericTestNode | CompiledGenericTestNode]],
        Optional[dict[str, ParsedSourceDefinition]]
]:
    """
    Parse the manifest.

    Only V4 manifest is supported.

    Parameters
    ----------
    manifest : dict[str, Any]
        The raw manifest.

    Returns
    -------
    dbt manifest parsed into a tuple of dicts containing: models_nodes, seed_nodes, test_nodes and source_nodes.
    Any of them may be `None` if they were not in the manifest.

    Raises
    ------
    NotImplementedError :
        If the dbt schema is not equal to the V4 manifest

    Source
    ------
    https://docs.getdbt.com/reference/artifacts/manifest-json
    """
    if manifest.get('nodes'):
        model_nodes = {
            node_name: CompiledModelNode(**node)
            if "compiled" in node.keys()
            else ParsedModelNode(**node)
            for node_name, node in manifest["nodes"].items()
            if node["resource_type"] == NodeType.Model
        }
        seed_nodes = {
            node_name: CompiledSeedNode(**node) if "compiled" in node.keys() else ParsedSeedNode(**node)
            for node_name, node in manifest["nodes"].items()
            if node["resource_type"] == NodeType.Seed
        }
        test_nodes = {
            node_name: CompiledGenericTestNode(**node)
            if "compiled" in node.keys()
            else ParsedGenericTestNode(**node)
            for node_name, node in manifest["nodes"].items()
            if node["resource_type"] == NodeType.Test
        }
    else:
        model_nodes = None
        seed_nodes = None
        test_nodes = None

    if manifest.get('sources'):
        source_nodes: Optional[dict] = {
            source_name: ParsedSourceDefinition(**source)
            for source_name, source in manifest["sources"].items()
            if source['resource_type'] == NodeType.Source
        }
    else:
        source_nodes = None
    return model_nodes, seed_nodes, test_nodes, source_nodes


def parse_run_results(run_results: dict[str, Any]) -> list[RunResultOutput]:
    """
    Parse the run results.

    Only V4 run results is supported.

    Parameters
    ----------
    run_results : dict[str, Any]
        The raw run results.

    Returns
    -------
    out : list[RunResultOutput]
        The parsed run results.

    Raises
    ------
    NotImplementedError :
        If the dbt schema is not equal to the V4 run results.

    Source
    ------
    https://docs.getdbt.com/reference/artifacts/run-results-json
    """
    parsed_run_results = [RunResultOutput(**result) for result in run_results["results"]]
    return parsed_run_results

def create_nodes_to_tests_mapping(
    model_nodes: dict[str, ParsedModelNode],
    test_nodes: Optional[dict[str, CompiledGenericTestNode | ParsedGenericTestNode]],
    run_results: list[RunResultOutput],
) -> dict[str, set[ParsedModelNode]]:
    """
    Map models to tests.

    Parameters
    ----------
    model_nodes : Dict[str: ParsedModelNode]
        The parsed model nodes.
    test_nodes : Dict[str: CompiledGenericTestNode]
        The compiled schema test nodes.
    run_results : List[RunResultOutput]
        The run results.

    Returns
    -------
    out : Dict[str, set[ParseModelNode]]
        A mapping from models to tests.
    """
    assert test_nodes, "No test nodes found in manifest.json. This could be because no test was implemented in dbt yet"

    test_unique_ids = [
        run_result.unique_id
        for run_result in run_results
        if run_result.unique_id in test_nodes.keys()
    ]

    models_that_tests_depends_on = {
        test_unique_id: set(test_nodes[test_unique_id].depends_on["nodes"])
        for test_unique_id in test_unique_ids
    }

    model_unique_ids = reduce(
        or_,
        [model_unique_ids for model_unique_ids in models_that_tests_depends_on.values()],
    )

    models_with_tests = defaultdict(set)
    for model_unique_id in model_unique_ids:
        for (
            test_unique_id,
            model_unique_ids_of_test,
        ) in models_that_tests_depends_on.items():
            if model_unique_id in model_unique_ids_of_test:
                models_with_tests[model_unique_id].add(test_unique_id)

    return models_with_tests
