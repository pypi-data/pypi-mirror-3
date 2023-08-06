"""
Test webhelper html wrappers.
"""
import unittest

from pepperedform.render import (text_field, checkbox_field,
        textarea_field, multiple_select_field, single_select_field, mapping,
        sequence, rename, primary_form_action, secondary_form_action,
        sequence_repeater, file_field)
from pepperedform.renderutils import FormRendererState, FormRenderer


class MockCallerStack(object):

    def _push_frame(*args, **kwargs):
        pass

    def _pop_frame(*args, **kwargs):
        pass


class MockContext(object):

    def _push_buffer(self, *args, **kwargs):
        # @TODO: Is this working ?
        self.buffers.append(self)

    def _pop_buffer(self):
        # @TODO: Is this working ?
        return self.buffers.pop()

    def __init__(self, caller=None):
        self.buffers = []
        self.attrs = {}
        self.out = []
        if caller:
            self.attrs['caller'] = caller
        self.caller_stack = MockCallerStack()

    def __getitem__(self, k):
        return self.attrs[k]

    def write(self, s):
        self.out.append(s)

    def getvalue(self):
        # @TODO: Is this working ? With push/pop buffer?
        return self.serialize()

    def serialize(self):
        return (u''.join(self.out)).encode('utf8')


class MockCaller(object):

    def __init__(self, body_text=u'', callback=None):
        self.body_text = body_text
        self.callback = callback

    def body(self, *args, **kwargs):
        if self.callback:
            self.callback(*args, **kwargs)
        else:
            return self.body_text

    def caller_stack(*args, **kwargs):
        pass


class TestRender(unittest.TestCase):

    def _get_mock_getter(self):
        def _mock_getter(items, name, if_missing=None):
            if items:
                return items.get(name, if_missing)
            return if_missing
        return _mock_getter

    def _get_form_renderer_state(self, defaults, errors=None):
        form = FormRenderer()
        return form.form_renderer_state(defaults, errors)

    def test_text_field_brainless(self):
        """
        Test text_field runs.
        """
        name = 'day'
        defaults = {
            name: '15'
        }
        context = MockContext()
        text_field(context, self._get_form_renderer_state(defaults), name)
        assert defaults[name] in context.serialize()

    def test_file_field_brainless(self):
        """
        Test file_field runs.
        """
        name = 'image'
        defaults = {}
        context = MockContext()
        file_field(context, self._get_form_renderer_state(defaults), name)
        assert name in context.serialize()

    def test_checkbox_field_brainless(self):
        name = 'is_today'
        defaults = {
            name: True
        }
        context = MockContext()
        checkbox_field(context, self._get_form_renderer_state(defaults), name)
        assert 'checked' in context.serialize()

    def test_textarea_field_brainless(self):
        name = 'coffee'
        defaults = {
            name: 'I think I will.'
        }
        context = MockContext()
        state = self._get_form_renderer_state(defaults)
        textarea_field(context, state, name)
        assert defaults[name] in context.serialize()

    def test_single_select_field_brainless(self):
        name = 'roast'
        selected_value = 'dark'
        defaults = {
            name: selected_value,
        }
        options = [(selected_value, 'Dark'), ('light', 'Light'), ('medium', 'Medium')]
        context = MockContext()
        state = self._get_form_renderer_state(defaults)
        single_select_field(context, state, name, options=options)
        html = context.serialize()
        assert 'selected=' in html, html

    def test_multiple_select_field_brainless(self):
        name = 'roast'
        defaults =  {
            name: ['dark', 'light']
        }
        options = [('dark', 'Dark'), ('light', 'Light'), ('medium', 'Medium')]
        context = MockContext()
        state = self._get_form_renderer_state(defaults)
        multiple_select_field(context, state, name, options=options)
        html = context.serialize()
        assert html.count('selected=') == 2, html

    def test_mapping_brainless(self):
        mapping_name = 'coffee'
        field_name = 'roast'
        field_value = 'dark'
        defaults = {
            mapping_name: {
                field_name: field_value
            }
        }
        # @TODO: Closure references context, this is pretty horrid.
        # We should clean up the mocks.
        def caller(state):
            text_field(context, state, field_name)
        context = MockContext(caller=MockCaller(callback=caller))
        state = self._get_form_renderer_state(defaults)
        mapping(context, state, mapping_name)
        html = context.serialize()
        assert mapping_name in html, html
        assert field_name in html, html
        assert field_value in html, html

    def test_sequence_brainless(self):
        """ Test that the sequence wrapper works. """
        sequence_name = 'coffees'
        defaults = {
            sequence_name: ['French Roast'],
        }
        values = {
            'counter': 0
        }
        def callback(state):
            values[values['counter']] = state.field_value(None)
            values['counter'] += 1
        context = MockContext(caller=MockCaller(callback=callback))
        state = self._get_form_renderer_state(defaults)
        sequence(context, state, sequence_name)
        html = context.serialize()
        assert sequence_name in html, html
        self.assertEquals(values[0], 'French Roast',
                'Only one value in list so value at 0 is French Roast')
        # callback should be called once.
        self.assertEquals(values['counter'], 1)

    def test_sequence_repeater_brainless(self):
        """ Test that the sequence repeater wrapper works. """
        sequence_name = 'coffees'
        defaults = {
            sequence_name: ['French Roast']
        }
        values = {
            'counter': 0
        }
        def callback(state):
            values[values['counter']] = state.field_value(None)
            values['counter'] += 1
        context = MockContext(caller=MockCaller(callback=callback))
        state = self._get_form_renderer_state(defaults)
        sequence_repeater(context, state, sequence_name)
        html = context.serialize()
        assert sequence_name in html, html
        self.assertEquals(values[0], None,
                'Template has no value so value at 0 is None.')
        self.assertEquals(values[1], 'French Roast',
                'Only one value in actual list so value at 1 is French Roast')
        # callback should be called twice.
        self.assertEquals(values['counter'], 2)

    def test_primary_form_action(self):
        """ Test that a primary form action is displayed. """
        state = self._get_form_renderer_state({})
        context = MockContext()
        value = u'Update'
        primary_form_action(context, state, value)
        assert value in context.serialize()

    def test_secondary_form_action(self):
        """ Test that a secondary form action is displayed. """
        context = MockContext()
        value = u'Cancel'
        state = self._get_form_renderer_state({})
        secondary_form_action(context, state, value)
        assert value in context.serialize()

