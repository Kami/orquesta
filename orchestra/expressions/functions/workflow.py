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

from orchestra import exceptions
from orchestra import states


def _get_current_task(context):
    current_task = context['__current_task'] or {}

    if not current_task:
        raise exceptions.ContextValueError('The current task is unset in the context.')

    return current_task


def task_state_(context, task_id):
    task_flow = context['__flow'] or {}
    task_flow_item_idx = task_flow['tasks'].get(task_id)

    if task_flow_item_idx is None:
        return states.UNSET

    task_flow_item = task_flow['sequence'][task_flow_item_idx]

    if task_flow_item is None:
        return states.UNSET

    return task_flow_item.get('state', states.UNSET)


def succeeded_(context):
    current_task = _get_current_task(context)

    return (task_state_(context, current_task.get('id')) == states.SUCCEEDED)


def failed_(context):
    current_task = _get_current_task(context)

    return (task_state_(context, current_task.get('id')) == states.FAILED)


def completed_(context):
    current_task = _get_current_task(context)

    return (task_state_(context, current_task.get('id')) in states.COMPLETED_STATES)
