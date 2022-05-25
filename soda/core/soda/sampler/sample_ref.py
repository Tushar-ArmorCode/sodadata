from __future__ import annotations

from soda.sampler.sample_schema import SampleSchema


class SampleRef:
    def __init__(
        self,
        # Sample display name for UIs
        name: str,
        schema: SampleSchema,
        total_row_count: int,
        stored_row_count: int,
        type: str,
        soda_cloud_file_id: str | None = None,
        message: str | None = None,
        link: str | None = None,
    ):
        self.name: str = name
        self.schema = schema
        self.total_row_count: int = total_row_count
        self.stored_row_count: int = stored_row_count
        self.type: str = type
        self.soda_cloud_file_id: str | None = soda_cloud_file_id
        self.message: str | None = message
        self.link: str | None = link

    def __str__(self) -> str:
        column_count = f"{len(self.schema.columns)}x" if self.schema else ''
        sample_dimension = f"{column_count}({self.stored_row_count}/{self.total_row_count})"
        return " ".join(
            [
                e
                for e in [self.type, self.soda_cloud_file_id, self.message, self.link, sample_dimension]
                if e is not None
            ]
        )

    def get_cloud_diagnostics_dict(self):
        column_dicts = (
            [column.get_cloud_dict() for column in self.schema.columns]
            if self.schema
            else None
        )
        sample_ref_dict = {
            "columns": column_dicts,
            "totalRowCount": self.total_row_count,
            "storedRowCount": self.stored_row_count,
        }
        if self.soda_cloud_file_id is None:
            sample_ref_dict["reference"] = {"type": "noFile"}
        else:
            sample_ref_dict["reference"] = {"type": "sodaCloudStorage", "fileId": self.soda_cloud_file_id}

        if self.message:
            sample_ref_dict["reference"] = {"type": "externalStorage", "message": self.message, "link": self.link}
        return sample_ref_dict
