"""
Non-mako utility functions used during rendering.
"""


def build_id_from_stack(id_stack, name):
    """ Combine all the parts in the id stack with the given name. """
    return u'_'.join(id_stack + [name])


def build_id(render_kwargs, name):
    """ Build a DOM id for an html tag. """
    return build_id_from_stack(render_kwargs['id_stack'], name)


def sequence_getter(items, name, if_missing=None):
    """ A sequence should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items
    return if_missing


def rename_getter(items, name, if_missing=None):
    """ A rename wrapper should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items
    return if_missing

    
def mapping_getter(items, name, if_missing=None):
    """  A mapping should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items.get(name, if_missing)
    return if_missing


def make_start_token(name, type_):
    """ Makes the special token used by peppercorn to group things. """
    value = u'{0}:{1}'.format(name, type_)
    return value


def field_error(render_kwargs, name, if_missing=None):
    """ Gets the error for this field out of the render_kwargs. """
    return render_kwargs['getter'](render_kwargs['errors'], name, if_missing=if_missing)


def field_value(render_kwargs, name, if_missing=None):
    """ Gets the value for this field out of the render_kwargs. """
    return render_kwargs['getter'](render_kwargs['defaults'], name, if_missing=if_missing)
