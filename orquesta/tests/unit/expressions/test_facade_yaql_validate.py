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

from orquesta.tests.unit import base as test_base


class YAQLFacadeValidationTest(test_base.ExpressionFacadeEvaluatorTest):

    def test_basic_validate(self):
        self.assertListEqual([], self.validate(None))
        self.assertListEqual([], self.validate('<% 1 %>'))
        self.assertListEqual([], self.validate('<% abc %>'))
        self.assertListEqual([], self.validate('<% 1 + 2 %>'))
        self.assertListEqual([], self.validate('<% ctx().foo %>'))
        self.assertListEqual([], self.validate('<% ctx(foo) %>'))
        self.assertListEqual([], self.validate('<% ctx().a1 + ctx(a2) %>'))

    def test_parse_error(self):
        expr = '<% <% ctx().foo %> %>'
        errors = self.validate(expr)

        self.assertEqual(1, len(errors))
        self.assertIn('Parse error', errors[0]['message'])

    def test_lexical_error(self):
        expr = '<% {"a": 123} %>'
        errors = self.validate(expr)

        self.assertEqual(1, len(errors))
        self.assertIn('Lexical error', errors[0]['message'])

    def test_multiple_errors(self):
        expr = '<% 1 +/ 2 %> and <% {"a": 123} %>'
        errors = self.validate(expr)

        self.assertEqual(2, len(errors))
        self.assertIn('Parse error', errors[0]['message'])
        self.assertIn('Lexical error', errors[1]['message'])

    def test_list_validate(self):
        self.assertListEqual([], self.validate([]))

        target = ['<% 1 %>', 'xyz', 123, True]
        self.assertListEqual([], self.validate(target))

        target = ['<% 1 %>', ['<% a %>', 'x']]
        self.assertListEqual([], self.validate(target))

        target = ['<% 1 %>', ['<% a %>', 'x'], {'k1': '<% 3 %>'}]
        self.assertListEqual([], self.validate(target))

    def test_list_multiple_errors(self):
        target = ['<% 1 +/ 2 %>', ['<% <% ctx().foo %>'], {'k1': '<% {"a": 1} %>'}]
        result = self.validate(target)
        self.assertEqual(3, len(result))

    def test_dict_validate(self):
        self.assertListEqual([], self.validate({}))

        target = {
            'k1': '<% 1 %>',
            'k2': 'foobar',
            '<% k3 %>': 789,
            'k4': ['<% abc %>', 'xyz', 123, False, {'k': 'v'}],
            'depth-1': {
                'depth-1-1': {
                    'depth-1-1-2': '<% ctx().a1 + ctx(a2) %>',
                    'depth-1-1-3': ['<% ctx().foobar %>', 'xyz']
                }
            }
        }

        self.assertListEqual([], self.validate(target))

    def test_dict_multiple_errors(self):
        target = {
            'k1': '<% 1 +/ 2 %>',
            'k2': 'foobar',
            '<% <% ctx().foo %>': 789,
            'k4': ['<% abc %>', 'xyz', 123, False, {'k': 'v'}],
            'depth-1': {
                'depth-1-1': {
                    'depth-1-1-2': '<% {"a": 1} %>',
                    'depth-1-1-3': ['<% ctx().foobar %>', '<% 3 +/ 4 %>']
                }
            }
        }

        result = self.validate(target)
        self.assertEqual(4, len(result))
