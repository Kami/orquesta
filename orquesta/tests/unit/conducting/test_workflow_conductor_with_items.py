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

from orquesta import conducting
from orquesta.specs import native as native_specs
from orquesta import statuses
from orquesta.tests.unit import base as test_base


class WorkflowConductorWithItemsTest(test_base.WorkflowConductorWithItemsTest):

    def test_empty_items_list(self):
        wf_def = """
        version: 1.0

        vars:
          - xs: []

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': []}
        task_action_specs = []

        mock_ac_ex_statuses = []
        expected_task_statuses = [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

        # Assert the workflow output is correct.
        expected_output = {'items': []}
        self.assertDictEqual(conductor.get_workflow_output(), expected_output)

    def test_basic_items_list(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED] * 4
        expected_task_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

        # Assert the workflow output is correct.
        expected_output = {'items': task_ctx['xs']}
        self.assertDictEqual(conductor.get_workflow_output(), expected_output)

    def test_basic_items_list_with_different_types(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - null
              - ""
              - foobar
              - 0
              - 1
              - 123
              - 123.456
              - False
              - True
              - {}
              - {'foobar': 'fubar'}
              - []
              - ['foobar', 'fubar']

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'

        task_ctx = {
            'xs': [
                None,
                '',
                'foobar',
                0,
                1,
                123,
                123.456,
                False,
                True,
                {},
                {'foobar': 'fubar'},
                [],
                ['foobar', 'fubar']
            ]
        }

        task_action_specs = []
        for idx, item in enumerate(task_ctx['xs']):
            task_action_specs.append(
                {'action': 'core.echo', 'input': {'message': item}, 'item_id': idx}
            )

        items_count = len(task_ctx['xs'])
        mock_ac_ex_statuses = [statuses.SUCCEEDED] * items_count
        expected_task_statuses = [statuses.RUNNING] * (items_count - 1) + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * (items_count - 1) + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

        # Assert the workflow output is correct.
        expected_output = {'items': task_ctx['xs']}
        self.assertDictEqual(conductor.get_workflow_output(), expected_output)

    def test_basic_items_list_with_concurrency(self):
        wf_def = """
        version: 1.0

        vars:
          - concurrency: 2
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with:
              items: <% ctx(xs) %>
              concurrency: <% ctx(concurrency) %>
            action: core.echo message=<% item() %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        concurrency = 2

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum'], 'concurrency': 2}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED] * 4
        expected_task_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses,
            concurrency=concurrency
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

    def test_multiple_items_list(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - foo
              - fu
              - marco
          - ys:
              - bar
              - bar
              - polo

        tasks:
          task1:
            with: x, y in <% zip(ctx(xs), ctx(ys)) %>
            action: core.echo message=<% item(x) + item(y) %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['foo', 'fu', 'marco'], 'ys': ['bar', 'bar', 'polo']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'foobar'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fubar'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'marcopolo'}, 'item_id': 2},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED] * 3
        expected_task_statuses = [statuses.RUNNING] * 2 + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * 2 + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            [i[0] + i[1] for i in zip(task_ctx['xs'], task_ctx['ys'])],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

        # Assert the workflow output is correct.
        expected_output = {'items': ['foobar', 'fubar', 'marcopolo']}
        self.assertDictEqual(conductor.get_workflow_output(), expected_output)

    def test_multiple_items_list_with_different_types(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - null
              - ""
              - foobar
              - 0
              - 1
              - 123
              - 123.456
              - False
              - True
              - {}
              - {'foobar': 'fubar'}
              - []
              - ['foobar', 'fubar']
          - ys:
              - null
              - ""
              - foobar
              - 0
              - 1
              - 123
              - 123.456
              - False
              - True
              - {}
              - {'foobar': 'fubar'}
              - []
              - ['foobar', 'fubar']
        tasks:
          task1:
            with: x, y in <% zip(ctx(xs), ctx(ys)) %>
            action: core.foobar
            input:
              x: <% item(x) %>
              y: <% item(y) %>
            next:
              - publish:
                  - items: <% result() %>

        output:
          - items: <% ctx(items) %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'

        task_ctx = {
            'xs': [
                None,
                '',
                'foobar',
                0,
                1,
                123,
                123.456,
                False,
                True,
                {},
                {'foobar': 'fubar'},
                [],
                ['foobar', 'fubar']
            ],
            'ys': [
                None,
                '',
                'foobar',
                0,
                1,
                123,
                123.456,
                False,
                True,
                {},
                {'foobar': 'fubar'},
                [],
                ['foobar', 'fubar']
            ]
        }

        task_action_specs = []
        for idx, pair in enumerate(zip(task_ctx['xs'], task_ctx['ys'])):
            task_action_specs.append(
                {'action': 'core.foobar', 'input': {'x': pair[0], 'y': pair[1]}, 'item_id': idx}
            )

        items_count = len(task_ctx['xs'])
        mock_ac_ex_statuses = [statuses.SUCCEEDED] * items_count
        expected_task_statuses = [statuses.RUNNING] * (items_count - 1) + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * (items_count - 1) + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            list(zip(task_ctx['xs'], task_ctx['ys'])),
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

        # Assert the workflow output is correct.
        expected_output = {'items': [[i, j] for i, j in zip(task_ctx['xs'], task_ctx['ys'])]}
        self.assertDictEqual(conductor.get_workflow_output(), expected_output)

    def test_multiple_items_list_with_concurrency(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - foo
              - fu
              - marco
          - ys:
              - bar
              - bar
              - polo

        tasks:
          task1:
            with:
              items: x, y in <% zip(ctx(xs), ctx(ys)) %>
              concurrency: 1
            action: core.echo message=<% item(x) + item(y) %>
        """

        concurrency = 1

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['foo', 'fu', 'marco'], 'ys': ['bar', 'bar', 'polo']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'foobar'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fubar'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'marcopolo'}, 'item_id': 2},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED] * 3
        expected_task_statuses = [statuses.RUNNING] * 2 + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * 2 + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            [i[0] + i[1] for i in zip(task_ctx['xs'], task_ctx['ys'])],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses,
            concurrency=concurrency
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)

    def test_fail_one_and_only_item(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
        ]

        mock_ac_ex_statuses = [statuses.FAILED]
        expected_task_statuses = [statuses.FAILED]
        expected_workflow_statuses = [statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_failed_item_task_dormant_other_incomplete(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED, statuses.FAILED]
        expected_task_statuses = [statuses.RUNNING, statuses.FAILED]
        expected_workflow_statuses = [statuses.RUNNING, statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_failed_item_task_dormant_other_failed(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED, statuses.FAILED, statuses.FAILED]
        expected_task_statuses = [statuses.RUNNING, statuses.RUNNING, statuses.FAILED]
        expected_workflow_statuses = [statuses.RUNNING, statuses.RUNNING, statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_failed_item_task_active(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [
            statuses.SUCCEEDED,
            statuses.FAILED,
            statuses.SUCCEEDED,
            statuses.SUCCEEDED
        ]

        expected_task_statuses = [statuses.RUNNING] * 3 + [statuses.FAILED]

        expected_workflow_statuses = [statuses.RUNNING] * 3 + [statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_failed_item_task_dormant_with_concurrency(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with:
              items: <% ctx(xs) %>
              concurrency: 2
            action: core.echo message=<% item() %>
        """

        concurrency = 2

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED, statuses.FAILED]
        expected_task_statuses = [statuses.RUNNING, statuses.FAILED]
        expected_workflow_statuses = [statuses.RUNNING, statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses,
            concurrency=concurrency
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_failed_item_task_active_with_concurrency(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          task1:
            with:
              items: <% ctx(xs) %>
              concurrency: 2
            action: core.echo message=<% item() %>
        """

        concurrency = 2

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [
            statuses.SUCCEEDED,
            statuses.FAILED,
            statuses.SUCCEEDED,
            statuses.SUCCEEDED
        ]

        expected_task_statuses = [statuses.RUNNING] * 3 + [statuses.FAILED]

        expected_workflow_statuses = [statuses.RUNNING] * 3 + [statuses.FAILED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses,
            concurrency=concurrency
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow failed.
        self.assertEqual(conductor.get_workflow_status(), statuses.FAILED)

    def test_task_cycle(self):
        wf_def = """
        version: 1.0

        vars:
          - xs:
              - fee
              - fi
              - fo
              - fum

        tasks:
          init:
            next:
              - do: task1
          task1:
            with: <% ctx(xs) %>
            action: core.echo message=<% item() %>
            next:
              - when: <% failed() %>
                do: task1
        """

        spec = native_specs.WorkflowSpec(wf_def)
        self.assertDictEqual(spec.inspect(), {})

        conductor = conducting.WorkflowConductor(spec)
        conductor.request_workflow_status(statuses.RUNNING)

        # Get pass the init task, required for bootstrapping self looping task..
        self.forward_task_statuses(conductor, 'init', [statuses.RUNNING, statuses.SUCCEEDED])

        # Mock the action execution for each item and assert expected task statuses.
        task_route = 0
        task_name = 'task1'
        task_ctx = {'xs': ['fee', 'fi', 'fo', 'fum']}

        task_action_specs = [
            {'action': 'core.echo', 'input': {'message': 'fee'}, 'item_id': 0},
            {'action': 'core.echo', 'input': {'message': 'fi'}, 'item_id': 1},
            {'action': 'core.echo', 'input': {'message': 'fo'}, 'item_id': 2},
            {'action': 'core.echo', 'input': {'message': 'fum'}, 'item_id': 3},
        ]

        mock_ac_ex_statuses = [statuses.SUCCEEDED, statuses.FAILED]
        expected_task_statuses = [statuses.RUNNING, statuses.FAILED]
        expected_workflow_statuses = [statuses.RUNNING] * 2

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is reset in staging.
        staged_task = conductor.workflow_state.get_staged_task(task_name, task_route)
        self.assertIsNotNone(staged_task)
        self.assertNotIn('items', staged_task)

        # Assert the workflow is still running.
        self.assertEqual(conductor.get_workflow_status(), statuses.RUNNING)

        # Mock the second task execution.
        mock_ac_ex_statuses = [statuses.SUCCEEDED] * 4
        expected_task_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]
        expected_workflow_statuses = [statuses.RUNNING] * 3 + [statuses.SUCCEEDED]

        self.assert_task_items(
            conductor,
            task_name,
            task_route,
            task_ctx,
            task_ctx['xs'],
            task_action_specs,
            mock_ac_ex_statuses,
            expected_task_statuses,
            expected_workflow_statuses
        )

        # Assert the task is removed from staging.
        self.assertIsNone(conductor.workflow_state.get_staged_task(task_name, task_route))

        # Assert the workflow succeeded.
        self.assertEqual(conductor.get_workflow_status(), statuses.SUCCEEDED)
