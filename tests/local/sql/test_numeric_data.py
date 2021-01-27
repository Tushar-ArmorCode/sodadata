#  Copyright 2021 Soda
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from tests.common.sql_test_case import SqlTestCase
from sodasql.scan.metric import Metric


class TestNumericData(SqlTestCase):

    def test_overflow(self):
        self.sql_recreate_table(
            [self.sql_declare_big_integer_column("name")],
            ["(9223372036854775807)",
             "(9223372036854775807)"])

        self.scan({
            'metrics': [
                Metric.SUM,
                Metric.AVG
            ]
        })

    def test_numeric_parsing(self):
        self.sql_recreate_table(
            [self.sql_declare_string_column("name")],
            ["('1%')",
             "('2.0%')",
             "('3,0%')"])

        scan_result = self.scan({
            'metrics': [
                Metric.INVALID_COUNT,
                Metric.INVALID_PERCENTAGE,
                Metric.VALID_COUNT,
                Metric.VALID_PERCENTAGE,
                Metric.HISTOGRAM,
                Metric.MIN,
                Metric.MAX
            ],
            'columns': {
                'name': {
                    'valid_format': 'number_percentage'
                }
            }
        })

        self.assertEqual(scan_result.get(Metric.VALUES_COUNT, 'name'), 3)
        self.assertEqual(scan_result.get(Metric.INVALID_COUNT, 'name'), 0)
        self.assertEqual(scan_result.get(Metric.INVALID_PERCENTAGE, 'name'), 0.0)
        self.assertEqual(scan_result.get(Metric.VALID_COUNT, 'name'), 3)
        self.assertEqual(scan_result.get(Metric.VALID_PERCENTAGE, 'name'), 100.0)
        self.assertEqual(scan_result.get(Metric.MIN, 'name'), 1)
        self.assertEqual(scan_result.get(Metric.MAX, 'name'), 3)
        self.assertAllNumeric(scan_result.get(Metric.HISTOGRAM)['boundaries'])
        self.assertAllNumeric(scan_result.get(Metric.HISTOGRAM)['frequencies'])
