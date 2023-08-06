import unittest

from pepperedform.renderutils import (sequence_getter, mapping_getter,
        make_start_token, FormRendererState, FormRenderer)


class TestRenderUtils(unittest.TestCase):

    def _get_mock_getter(self):
        def _mock_getter(items, name, if_missing=None):
            if items:
                return items.get(name, if_missing)
            return if_missing
        return _mock_getter

    def _get_renderer(self, **kwargs):
        return FormRenderer(**kwargs)

    def _get_renderer_state(self, defaults, errors=None, renderer=None):
        if not renderer:
            renderer = self._get_renderer()
        return renderer.form_renderer_state(defaults, errors)

    def test_push_id_stack(self):
        """ Stack should grow to 2 elements. """
        state = self._get_renderer_state({})
        state = state.mapping_descend('user')
        state = state.mapping_descend('identity')
        self.assertEqual(len(state.id_stack), 2)

    def test_build_id(self):
        """ Id stack should be glued together with spaces. """
        state = self._get_renderer_state({})
        state = state.mapping_descend('user')
        state = state.mapping_descend('identity')
        name = 'first_name'
        id_ = state.build_id(name)
        self.assertEqual(id_, 'user_identity_first_name')


    def test_sequence_getter_missing(self):
        items = None
        if_missing = tuple()
        result = sequence_getter(items, None, if_missing=if_missing)
        self.assertIs(result, if_missing,
                msg='Should return if_missing if items is falsy.')

    def test_sequence_getter(self):
        items = '15'
        if_missing = tuple()
        result = sequence_getter(items, None, if_missing=if_missing)
        self.assertEqual(result, '15',
                msg='Should return items if items is not falsy.')

    def test_mapping_getter_missing(self):
        items = {}
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        self.assertIs(result, if_missing,
                msg='Should return if_missing if name not in items.')

    def test_mapping_getter(self):
        items = {
            'day': '15'
        }
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        self.assertEqual(result, '15',
                'Should return value for key name in items if it exists.')

    def test_make_start_token(self):
        name = 'days'
        type_ = 'sequence'
        token = make_start_token(name, type_)
        self.assertEqual(token, 'days:sequence')

    def test_field_value(self):
        day_value = 1
        name = 'day'
        state = self._get_renderer_state({
            name: day_value
        })
        value = state.field_value(name)
        self.assertTrue(value, day_value)

    def test_sequence_descend(self):
        defaults = {
            'users': [{
                'name': u'Ian'
            },]
        }
        state = self._get_renderer_state(defaults)
        new_state = list(state.sequence_descend('users'))[0]
        self.assertEqual(new_state.field_value(None), defaults['users'][0])

    def test_field_error_missing(self):
        state = self._get_renderer_state({}, {})
        name = 'day'
        error = state.field_error(name)
        self.assertTrue(not error, 'No error should exist')

    def test_field_error(self):
        day_error = 'Today is the wrong day'
        name = 'day'
        state = self._get_renderer_state({
        }, {
            name: day_error
        })
        error = state.field_error(name)
        self.assertTrue(error and error == day_error)
