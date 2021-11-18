#  Copyright 2020 Soda
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import Optional
from sodasql.scan.dialect import Dialect


class MockDialect(Dialect):
    """Testing dialect without dialect specific methods.

    Used for non specific dialect tests.
    """
    def create_connection(self):
        pass

    def sql_columns_metadata_query(self, table_name: str) -> str:
        pass

    def sql_tables_metadata_query(self, limit: Optional[int] = None, filter: str = None):
        pass

    def is_text(self, column_type: str):
        pass

    def is_number(self, column_type: str):
        pass

    def is_time(self, column_type: str):
        pass
