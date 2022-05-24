from typing import List

from soda.sampler.sample_ref import SampleRef
from soda.sodacl.sample_tables_cfg import SampleTablesCfg


class SampleTablesResultTable:
    def __init__(self, table_name: str, data_source: str, sample_ref: SampleRef):
        self.table_name: str = table_name
        self.data_source: str = data_source
        self.sample_ref: sample_ref = sample_ref

    def get_cloud_dict(self) -> dict:
        cloud_dict = {
            "table": self.table_name,
            "dataSource": self.data_source,
            "sampleFile": self.sample_ref.get_cloud_diagnostics_dict(),
        }
        return cloud_dict


class SampleTablesResult:
    def __init__(self, sample_tables_cfg: SampleTablesCfg):
        self.sample_tables_cfg: SampleTablesCfg = sample_tables_cfg
        self.tables: List[SampleTablesResultTable] = []

    def create_table(self, table_name: str, data_source_name: str, sample_ref: SampleRef) -> SampleTablesResultTable:
        table = SampleTablesResultTable(table_name, data_source_name, sample_ref)
        self.tables.append(table)
        return table