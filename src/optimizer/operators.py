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
from enum import IntEnum, unique
from typing import List
from src.parser.table_ref import TableRef


@unique
class OperatorType(IntEnum):
    """
    Manages enums for all the operators supported
    """
    LOGICALGET = 1,
    LOGICALFILTER = 2,
    LOGICALPROJECT = 3,


class Operator:
    """Base class for logital plan of operators

    Arguments:
        op_type: {OperatorType} -- {the opr type held by this node}
        children: {List} -- {the list of operator children for this node}
    """

    def __init__(self, op_type: OperatorType, children: List):
        self._type = op_type
        self._children = children

    def append_child(self, child: Operator):
        if self._children is None:
            self._children = []

        self._children.append(child)

    @property
    def children(self):
        return self._children

    @property
    def type(self):
        return self._type


class LogicalGet(Operator):
    def __init__(self, video: TableRef, catalog_entry: 'type',
                 children: List = None):
        super().__init__(OperatorType.LOGICALGET, children)
        self._video = video
        self._catalog_entry = catalog_entry


class LogicalFilter(Operator):
    def __init__(self, predicate: 'AbstractExpression', children: List = None):
        super().__init__(OperatorType.LOGICALFILTER, children)
        self._predicate = predicate


class LogicalProject(Operator):
    def __init__(self, target_list: List['AbstractExpression'],
                 children: List = None):
        super().__init__(OperatorType.LOGICALPROJECT, children)
        self._target_list = target_list
