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

from orquesta.tests.unit.composition.mistral import base


class BasicWorkflowComposerTest(base.MistralWorkflowComposerTest):

    def test_sequential(self):
        wf_name = 'sequential'

        expected_wf_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_graph(wf_name, expected_wf_graph)

        expected_wf_ex_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_ex_graph(wf_name, expected_wf_ex_graph)

    def test_parallel(self):
        wf_name = 'parallel'

        expected_wf_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                },
                {
                    'id': 'task4'
                },
                {
                    'id': 'task5'
                },
                {
                    'id': 'task6'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                [],
                [
                    {
                        'id': 'task5',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task4',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task6',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task5',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_graph(wf_name, expected_wf_graph)

        expected_wf_ex_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                },
                {
                    'id': 'task4'
                },
                {
                    'id': 'task5'
                },
                {
                    'id': 'task6'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                [],
                [
                    {
                        'id': 'task5',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task4',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task6',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task5',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_ex_graph(wf_name, expected_wf_ex_graph)

    def test_branching(self):
        wf_name = 'branching'

        expected_wf_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                },
                {
                    'id': 'task4'
                },
                {
                    'id': 'task5'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    },
                    {
                        'id': 'task4',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                [],
                [
                    {
                        'id': 'task5',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task4',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_graph(wf_name, expected_wf_graph)

        expected_wf_ex_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 'task1'
                },
                {
                    'id': 'task2'
                },
                {
                    'id': 'task3'
                },
                {
                    'id': 'task4'
                },
                {
                    'id': 'task5'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'task2',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    },
                    {
                        'id': 'task4',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task1',
                            condition='on-success'
                        )
                    }
                ],
                [
                    {
                        'id': 'task3',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task2',
                            condition='on-success'
                        )
                    }
                ],
                [],
                [
                    {
                        'id': 'task5',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            'task4',
                            condition='on-success'
                        )
                    }
                ],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_ex_graph(wf_name, expected_wf_ex_graph)

    def test_decision_tree(self):
        wf_name = 'decision'

        expected_wf_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 't1'
                },
                {
                    'id': 'a'
                },
                {
                    'id': 'b'
                },
                {
                    'id': 'c'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'a',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% ctx().which = 'a' %>"
                        )
                    },
                    {
                        'id': 'b',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% ctx().which = 'b' %>"
                        )
                    },
                    {
                        'id': 'c',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% not ctx().which in list(a, b) %>"
                        )
                    }
                ],
                [],
                [],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_graph(wf_name, expected_wf_graph)

        expected_wf_ex_graph = {
            'directed': True,
            'graph': {},
            'nodes': [
                {
                    'id': 't1'
                },
                {
                    'id': 'a'
                },
                {
                    'id': 'b'
                },
                {
                    'id': 'c'
                }
            ],
            'adjacency': [
                [
                    {
                        'id': 'a',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% ctx().which = 'a' %>"
                        )
                    },
                    {
                        'id': 'b',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% ctx().which = 'b' %>"
                        )
                    },
                    {
                        'id': 'c',
                        'key': 0,
                        'criteria': self.compose_seq_expr(
                            't1',
                            condition='on-success',
                            expr="<% not ctx().which in list(a, b) %>"
                        )
                    }
                ],
                [],
                [],
                []
            ],
            'multigraph': True
        }

        self.assert_compose_to_wf_ex_graph(wf_name, expected_wf_ex_graph)
