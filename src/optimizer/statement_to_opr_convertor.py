# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from src.optimizer.operators import LogicalGet, LogicalFilter, LogicalProject
from src.parser.eva_statement import AbstractStatement
from src.parser.select_statement import SelectStatement
from src.optimizer.optimizer_utils import (bind_table_ref, bind_columns_expr,
                                           bind_predicate_expr)


class StatementToPlanConvertor():
    def __init__(self):
        self._plan = None

    def visit_table_ref(self, video: 'TableRef'):
        """Bind table ref object and convert to Logical get operator

        Arguments:
            video {TableRef} -- [Input table ref object created by the parser]
        """
        catalog_vid_metadata_id = bind_table_ref(video.info)

        get_opr = LogicalGet(video, catalog_vid_metadata_id)
        self._plan = get_opr

    def visit_select(self, statement: AbstractStatement):
        """convertor for select statement

        Arguments:
            statement {AbstractStatement} -- [input select statement]
        """
        # Create a logical get node
        video = statement.from_table
        if video is not None:
            self.visit_table_ref(video)

        # Filter Operator
        predicate = statement.where_clause
        if predicate is not None:
            # Binding the expression
            bind_predicate_expr(predicate)
            filter_opr = LogicalFilter(predicate)
            filter_opr.append_child(self._plan)
            self._plan = filter_opr

        # Projection operator
        select_columns = statement.target_list

        # ToDO
        # add support for SELECT STAR
        if select_columns is not None:
            # Bind the columns using catalog
            bind_columns_expr(select_columns)
            projection_opr = LogicalProject(select_columns)
            projection_opr.append_child(self._plan)
            self._plan = projection_opr

    def visit(self, statement: AbstractStatement):
        """Based on the instance of the statement the corresponding
           visit is called.
           The logic is hidden from client.

        Arguments:
            statement {AbstractStatement} -- [Input statement]
        """
        if isinstance(statement, SelectStatement):
            self.visit_select(statement)

    @property
    def plan(self):
        return self._plan
