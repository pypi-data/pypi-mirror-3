"""
Test tools for using formprocess handlers.
"""
from webob.multidict import MultiDict
from pepperedform.handler import (set_closed, prepare_for_peppercorn,
        parse_with_peppercorn)


class DummyHandler(object):
    pass


class DummyState(object):
    pass


class TestHandlerTools(object):
        
    def test_set_closed(self):
        hook = set_closed(True)
        handler = DummyHandler()
        state = DummyState()
        fill_kwargs = {}
        errors = {}
        defaults = {}
        new_fill_kwargs = hook(handler, defaults, errors, state, fill_kwargs)
        assert new_fill_kwargs['closed']

    def test_parse_for_peppercorn(self):
        handler = DummyHandler()
        state = DummyState()
        unsafe_params = MultiDict([
            ('__start__', 'days:sequence'),
            ('__start__', 'day:sequence'),
            ('day', '1'),
            ('__end__', 'day:sequence'),
            ('__start__', 'sequence'),
            ('day', '2'),
            ('__end__', 'day:sequence'),
            ('__start__', 'day:sequence'),
            ('day', '3'),
            ('__end__', 'day:sequence'),
            ('__end__', 'days:sequence')])
        new_defaults = parse_with_peppercorn(handler, unsafe_params, state)
        assert len(new_defaults['days']) == 3

    def test_prepare_for_peppercorn(self):
        handler = DummyHandler()
        state = DummyState()
        defaults = {}
        errors = {}
        fill_kwargs = {}
        new_fill_kwargs = prepare_for_peppercorn(handler, defaults, errors, state,
                fill_kwargs)
        assert new_fill_kwargs.get('id_stack') == [], 'id_stack must be empty list'
        assert new_fill_kwargs.get('getter'), 'getter must be defined'
