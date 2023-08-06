"""
Hooks for use with the Handler class in formprocess.
"""
from peppercorn import parse

from pepperedform.render import mapping_getter


def parse_with_peppercorn(handler_instance, unsafe_params, state):
    """
    Extract form params in the peppercorn format into structured params.
    
    Note: This should be used as a default_filter_hook in a formprocess
        handler.
    """
    return parse(unsafe_params.items())


def prepare_for_peppercorn(handler_instance, defaults, errors, state,
        fill_kwargs):
    """
    Add settings needed for rendering the form so peppercorn can process it.

    Note: This should be used as a customize_fill_kwargs_hook in a formprocess
        handler.
    """
    # Code to build ids for html depends on this being set.
    fill_kwargs['id_stack'] = []
    # Used to get the defaults and errors.
    fill_kwargs['getter'] = mapping_getter
    return fill_kwargs


def set_css_classes(override_css_classes=None):
    def _set_css_classes(handler_instance, defaults, errors, state, fill_kwargs):
        # Only override them if we were given some classes.
        if override_css_classes:
            fill_kwargs['css_classes'] = override_css_classes
        return fill_kwargs
    return _set_css_classes

        
def set_closed(closed):
    """
    Create a closure to set a boolean in the fillkwargs to close tags or not.
    """
    def _set_closed(handler_instance, defaults, errors, state, fill_kwargs):
        fill_kwargs['closed'] = closed
        return fill_kwargs
    return _set_closed
