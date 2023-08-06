"""
Test webhelper html wrappers.
"""
from pepperedform.render import (text_field, checkbox_field,
        textarea_field, multiple_select_field, single_select_field, mapping, 
        sequence, rename, primary_form_action, secondary_form_action)


class MockCallerStack(object):
    def _push_frame(*args, **kwargs):
        pass

    def _pop_frame(*args, **kwargs):
        pass


class MockContext(object):
    
    def __init__(self, caller=None):
        self.attrs = {}
        self.out = []
        if caller:
            self.attrs['caller'] = caller
        self.caller_stack = MockCallerStack()

    def __getitem__(self, k):
        return self.attrs[k]

    def write(self, s):
        self.out.append(s)
    
    def serialize(self):
        return (u''.join(self.out)).encode('utf8')


class MockCaller(object):

    def __init__(self, body_text):
        self.body_text = body_text

    def body(self, *args, **kwargs):
        return self.body_text

    def caller_stack(*args, **kwargs):
        pass


class TestRender(object):

    def _get_mock_getter(self):
        def _mock_getter(items, name, if_missing=None):
            if items:
                return items.get(name, if_missing)
            return if_missing
        return _mock_getter

    def test_text_field_brainless(self):
        """
        Do a brainless test to see if these have runtime errors.
        """
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'day': '15'
            },
            'id_stack': [],
            'errors': None
        }
        name = 'day'
        context = MockContext()
        text_field(context, render_kwargs, name)
        assert context.serialize()

    def test_checkbox_field_brainless(self):
        name = 'is_today'
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                name: True
            },
            'id_stack': [],
            'errors': None
        }
        context = MockContext()
        checkbox_field(context, render_kwargs, name)
        assert context.serialize()

    def test_textarea_field_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'coffee': 'I think I will.'
            },
            'id_stack': [],
            'errors': None
        }
        name = 'coffee'
        context = MockContext()
        textarea_field(context, render_kwargs, name)
        assert context.serialize()

    def test_single_select_field_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'roast': ['dark']
            },
            'id_stack': [],
            'errors': None
        }
        name = 'roast'
        options = [('dark', 'Dark'), ('light', 'Light'), ('medium', 'Medium')]
        context = MockContext()
        single_select_field(context, render_kwargs, name, options=options)
        assert context.serialize()

    def test_multiple_select_field_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'roast': ['dark', 'light']
            },
            'id_stack': [],
            'errors': None
        }
        name = 'roast'
        options = [('dark', 'Dark'), ('light', 'Light'), ('medium', 'Medium')]
        context = MockContext()
        multiple_select_field(context, render_kwargs, name, options=options)
        assert context.serialize()

    def test_mapping_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'roast': ['dark']
            },
            'errors': None,
            'id_stack': [],
            'closed': True,
            'errors': None
        }
        caller = MockCaller(u'Body Text')
        context = MockContext(caller=caller)
        assert mapping(context, render_kwargs, 'coffee') == ''
        assert context.serialize()

    def test_primary_form_action(self):
        render_kwargs = {}
        context = MockContext()
        primary_form_action(context, render_kwargs, u'Update')
        assert context.serialize()

    def test_secondary_form_action(self):
        render_kwargs = {}
        context = MockContext()
        secondary_form_action(context, render_kwargs, u'Cancel')
        assert context.serialize()
