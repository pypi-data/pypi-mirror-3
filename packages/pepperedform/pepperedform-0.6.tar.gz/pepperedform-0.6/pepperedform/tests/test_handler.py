"""
Test tools for using formprocess handlers.
"""
import unittest

from webob.multidict import MultiDict

from pepperedform.handler import parse_with_peppercorn, renderer_state_injector


class DummyHandler(object):
    pass


class DummyState(object):
    pass


class DummyFormRenderer(object):
    def form_renderer_state(self, *args, **kwargs):
        return dict(args=args, kwarg=kwargs)


class TestHandlerTools(unittest.TestCase):

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
        self.assertEqual(len(new_defaults['days']), 3)

    def test_renderer_state_injector(self):
        form_renderer = DummyFormRenderer()
        injector = renderer_state_injector(form_renderer, inject_at_key='test')
        fill_kwargs = {}
        defaults = {}
        errors = {}
        fill_kwargs = injector(None, defaults, errors, None, fill_kwargs)
        self.assertEqual(fill_kwargs['test']['args'], (defaults, errors))
