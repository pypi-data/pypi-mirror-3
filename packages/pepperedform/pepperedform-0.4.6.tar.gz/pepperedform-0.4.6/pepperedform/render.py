"""
Tools used when rendering the form.

The fields try to be flexible but if you want some heavy modification you are
probably better off just writing your own field and following or faking the
rules of render_kwargs.


About render_kwargs
===================

  All you wanted to know about render_kwargs:

  * REQUIRED KEYS
      getter -- callable that is used to get defaults and errors for contained
          things
      id_stack -- list of names of things above the current thing
      defaults -- None or dict/list/etc. of defaults
      errors -- None or dict/list/stringish of errors

  * OPTIONAL KEYS
      css_classes -- map from css class identifier to name of class to use
      _closed -- boolean flag determining if input tags should be closed
      field_part_orders -- map overrwide default_field_part_orders
      extra_renderers -- map from name of thing to render to callable

Field Extras
============

  * What is an example of an example?

    Date Ex: 10-11-1982

  * How would I use help?

    Use JS to roll the help text up and either show it when the input receives
    focus or when the help icon is clicked/hovered.

Field parts and their orders
============================

In order to support re-ordering of the structure of fields you can specify
the order of the parts.  The parts consist of input, label, help, example,
error and a special clear part.  The clear part just inject a div with
a clear class in order to allow floats to be cleared.  This part can occur
more than once in the given order.
"""
from types import StringTypes
from mako.runtime import supports_caller, capture
from webhelpers.misc import NotGiven
from webhelpers.html.builder import HTML
from webhelpers.html.tags import select

from pepperedform.renderutils import (build_id, sequence_getter, rename_getter, 
        mapping_getter, make_start_token, field_value, field_error)


SEQUENCE = u'sequence'
MAPPING = u'mapping'
RENAME = u'rename'


default_field_part_orders = {
    'checkbox_field': ('input', 'label', 'help', 'example', 'error'),
    None: ('label', 'help', 'example', 'input', 'error')
}
"""
Map from field type to list of field part names.
The None key designates the default order since not all field types will have an entry.

Overwrite these in the render_kwargs.
"""


tag = HTML.tag


default_css_classes = {
    'field_errors': 'field_errors',
    'password_field': 'password_field',
    'file_field': 'file_field',
    'checkbox_field': 'checkbox_field',
    'textarea_field': 'textarea_field',
    'hidden_field': 'hidden_field',
    'text_field': 'text_field',
    'single_select_field': 'single_select_field',
    'single_select_field': 'single_select_field',
    'single_select_list_field': 'single_select_list_field',
    'single_select_list_item': 'single_select_list_item',
    'multiple_select_field': 'multiple_select_field',
    'multiple_select_list_field': 'multiple_select_list_field',
    'multiple_select_list_item': 'multiple_select_list_item',
    'repeater': 'repeater',
    'template': 'template',
    'adder': 'adder',
    'remover': 'remover',
    'repetition': 'repetition',
    'repetitions': 'repetitions',
    'field_label': 'field_label',
    'field_help': 'field_help',
    'field_example': 'field_example',
    'clear': 'clear',
    'primary_form_action': 'primary_form_action',
    'secondary_form_action': 'secondary_form_action',
    'field_has_error': 'field_has_error',
}
"""
Notable css classes indexed by key.

Overwrite these in the render kwargs.
"""


def _to_css_class(css_classes):
    return ' '.join(css_classes)


def _determine_css_classes(render_kwargs, class_name,
            add_css_classes=None):
    """
    Determine the css classes to use by first checking the dict at the
        `css_classes` key in render_kwargs and then checking defaults in this
        module.
    """
    css_classes = None
    if 'css_classes' in render_kwargs:
        css_classes = render_kwargs['css_classes'].get(class_name, None)
    if not css_classes:
        css_classes = default_css_classes.get(class_name, None)
    # Wart to handle css classes as a string.
    if isinstance(css_classes, StringTypes):
        css_classes = set([css_classes])
    # Wart to handle css classes as a list or tuple.
    elif not isinstance(css_classes, set):
        css_classes = set(css_classes)
    if add_css_classes:
        css_classes.update(add_css_classes)
    return css_classes


def _determine_field_part_list(render_kwargs, field_parts, field_part_order, field_type=None):
    """
    Determine the order of the parts, such as label and input, in the HTML.

    Note: This can be overridden in the render_kwargs by the field_type in a
        dict at the `field_part_orders` key, use the field_type `None` to match
        all unmatched field types. If no field part order is found in the
        dict in render kwargs then defaults in this module are used.

    A special field part exists to to inject a clearing div.
    """
    if not field_part_order:
        if 'field_part_orders' in render_kwargs:
            if field_type:
                field_part_order = render_kwargs['field_part_orders'].get(field_type, None)
            if not field_part_order:
                field_part_order = render_kwargs['field_part_orders'].get(None, None)
    if not field_part_order:
        if field_type:
            field_part_order = default_field_part_orders.get(field_type, None)
        if not field_part_order:
            field_part_order = default_field_part_orders[None]
    field_part_list = []
    for field_part_name in field_part_order:
        # Hack in order to clear floats.
        if field_part_name == 'clear':
            clear_class = _determine_clear_class(render_kwargs, 'clear')
            field_part_list.append(tag('div', '', class_=clear_class, _closed=True))
        elif field_part_name in field_parts:
            # Flatten iterable field parts into the existing list.
            if type(field_parts[field_part_name]) in (list, tuple):
                field_part_list.extend(field_parts[field_part_name])
            else:
                field_part_list.append(field_parts[field_part_name])
    return field_part_list


def _render_field_errors(render_kwargs, name):
    """
    Return an error messages div or None, each error is wrapped in a span.
    """
    errors = field_error(render_kwargs, name)
    error_div = None
    if errors:
        error_spans = []
        if type(errors) in (list, tuple):
            for error in errors:
                error_spans.append(tag('span', error))
        else:
            error_spans.append(tag('span', errors))
        css_class = _to_css_class(_determine_css_classes(render_kwargs,
                'field_errors'))
        error_div = tag('div', *error_spans, class_=css_class)
    return error_div


def _determine_extra_field_parts(render_kwargs, field_parts, field_extras):
    """
    Build any extra field parts as necessary, such as an example or help.
    """
    extra_field_parts = {}
    if field_extras and 'example' in field_extras:
        example_css_class = _to_css_class(_determine_css_classes(render_kwargs,
                'field_example'))
        if 'extra_renderers' in render_kwargs and 'example' in \
                render_kwargs['extra_renderers']:
            renderer = render_kwargs['extra_renderers']['example']
            extra_field_parts['example'] = renderer(render_kwargs,
                    class_=example_css_class,
                    example=field_extras['example'])
        else:
            example = field_extras['example']
            if type(example) not in (list, tuple):
                example = [example]
            extra_field_parts['example'] = tag('span', *example,
                    class_=example_css_class)
    if field_extras and 'help' in field_extras:
        help_css_class = _to_css_class(_determine_css_classes(render_kwargs,
                'field_help'))
        if 'extra_renderers' in render_kwargs and 'help' in \
                render_kwargs['extra_renderers']:
            renderer = render_kwargs['extra_renderers']['help']
            extra_field_parts['help'] = renderer(render_kwargs,
                    class_=help_css_class, help=field_extras['help'])
        else:
            extra_field_parts['help'] = tag('span', field_extras['help'],
                    class_=help_css_class)
    return extra_field_parts


def primary_form_action(context, render_kwargs, value, css_classes=None,
            **attrs):
    """ Primary submit button -- Use this for the main action of the form. """
    attrs['class_'] = _to_css_class(_determine_css_classes(render_kwargs,
            'primary_form_action',
            add_css_classes=css_classes))
    attrs.setdefault('type', 'submit')
    closed = render_kwargs.get('closed', False)
    context.write(tag('input', value=value, _closed=closed, **attrs))
    return ''


def secondary_form_action(context, render_kwargs, value, tag_name='input', **attrs):
    """
    Seconary submit button -- Use this for an action that is less significant
    than the primary action.
    """
    attrs['class_'] = _to_css_class(_determine_css_classes(render_kwargs,
            'secondary_form_action'))
    if tag_name == 'input':
        attrs.setdefault('type', 'button')
        attrs.setdefault('value', value)
        attrs.setdefault('_closed', render_kwargs.get('closed', False))
    else:
        # Content inside the tags.
        attrs.setdefault('c', value)
    context.write(tag(tag_name, **attrs))
    return ''


def hidden_field(context, render_kwargs, name, value=NotGiven, id=NotGiven,
        field_part_order=None, **attrs):
    """ Standard input element of type hidden. """
    if value is NotGiven:
        value = field_value(render_kwargs, name)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    attrs['_closed'] = render_kwargs.get('closed', False)
    attrs['class_'] = _to_css_class(_determine_css_classes(render_kwargs,
            'hidden_field'))
    field_parts = {}
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='hidden', **attrs)
    error = _render_field_errors(render_kwargs, name)
    if error:
        field_parts['error'] = error
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    for field_part in field_part_list:
        context.write(field_part)
    return ''


def file_field(context, render_kwargs, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None, **attrs):
    """ Standard input element of type file. """
    field_parts = {}
    if value is NotGiven:
        value = field_value(render_kwargs, name)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    # If the label is None there will be no label.
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='file', **attrs)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'file_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def password_field(context, render_kwargs, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None, **attrs):
    """ Standard input element of type password. """
    if value is NotGiven:
        value = field_value(render_kwargs, name)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    field_parts = {}
    if field_extras:
        _inject_field_extras(field_parts, field_extras)
    attrs['_closed'] = render_kwargs.get('closed', False)
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='password', **attrs)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'password_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def text_field(context, render_kwargs, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None, **attrs):
    """ Standard input element of type text. """
    if value is NotGiven:
        value = field_value(render_kwargs, name)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='text', **attrs)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'text_field', add_css_classes=add_css_classes))
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def checkbox_field(context, render_kwargs, name, checked=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None, **attrs):
    """ Standard input element of type checkbox. """
    field_type = 'checkbox_field'
    if checked is NotGiven:
        checked = field_value(render_kwargs, name, False)
    if checked:
        checked = 'checked'
    else:
        checked = None
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts = {}
    field_parts['input'] = tag('input', name=name, value='1', checked=checked,
            id=id, type='checkbox', **attrs)
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts,
            field_part_order, field_type=field_type)
    css_class = _to_css_class(_determine_css_classes(render_kwargs, field_type,
            add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def textarea_field(context, render_kwargs, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=NotGiven, **attrs):
    """ Standard textarea element. """
    if field_classes is NotGiven:
        add_css_classes = set()
    else:
        add_css_classes = set(field_classes)
    field_type = 'textarea_field'
    if value is NotGiven:
        value = field_value(render_kwargs, name, u'')
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('textarea', value, name=name, id=id, **attrs)
    error = _render_field_errors(render_kwargs, name)
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs, field_type,
            add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def single_select_field(context, render_kwargs, name, options, value=NotGiven,
        id=NotGiven, label=NotGiven, field_extras=None, field_part_order=None, **attrs):
    """ Standard select element where multiple is not set. """
    if value is NotGiven:
        value = field_value(render_kwargs, name, NotGiven)
    if value is NotGiven:
        values = []
    else:
        values = [value]
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts = {}
    field_parts['input'] = select(name, values, options, id=id)
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'single_select_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def multiple_select_field(context, render_kwargs, name, options,
        values=NotGiven, id=NotGiven, label=NotGiven, field_extras=None,
        field_part_order=None, **attrs):
    """ Standard select element where multiple is set to true. """
    if values is NotGiven:
        values = field_value(render_kwargs, name, [])
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    field_parts['input'] = select(name, values, options, id=id, multiple=True)
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'multiple_select_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def multiple_select_list_field(context, render_kwargs, name, options,
        values=NotGiven, label=NotGiven, id=NotGiven, field_extras=None,
        field_part_order=None, **attrs):
    """ Wrap a list of input elements of type checkbox. """
    if values is NotGiven:
        values = field_value(render_kwargs, name, [])
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    closed = render_kwargs.get('closed', False)
    attrs['_closed'] = closed
    start_token = make_start_token(name, SEQUENCE)
    field_parts = {}
    # Start list now because peppercorn stuff must always wrap around the
    # field parts.
    field_part_list = []
    field_part_list.append(tag('input', type='hidden', name='__start__', value=start_token, _closed=closed))
    if label:
        field_parts['label'] = tag('legend', label)
    item_css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'multiple_select_list_item'))
    field_parts['input'] = []
    for index, option in enumerate(options):
        (option_value, option_label) = option
        if option_value in values:
            checked = 'checked'
        else:
            checked = None
        option_id = id + u'_' + unicode(option_value)
        field_parts['input'].append(tag('div',
                tag('input', name=name, value=option_value, id=option_id,
                        checked=checked, type='checkbox', **attrs),
                tag('label', option_label, for_=option_id), class_=item_css_class))
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list.extend(_determine_field_part_list(render_kwargs, field_parts, field_part_order))
    field_part_list.append(tag('input', type='hidden', name='__end__',
            value=start_token, _closed=closed))
    css_class = _to_css_classes(_determine_css_classes(render_kwargs,
            'multiple_select_list_field', add_css_classes=add_css_classes))
    context.write(tag('div', tag('fieldset', *field_part_list), class_=css_class))
    return ''


def single_select_list_field(context, render_kwargs, name, options,
        value=NotGiven, id=NotGiven, label=NotGiven, field_extras=None,
        field_part_order=None, **attrs):
    """ Wrap a list of input elements of type radio. """
    if value is NotGiven:
        value = field_value(render_kwargs, name)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = render_kwargs.get('closed', False)
    field_parts = {}
    if label:
        field_parts['label'] = tag('legend', label)
    item_css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'single_select_list_item'))
    field_parts['input'] = []
    for index, option in enumerate(options):
        (option_value, option_label) = option
        checked = option_value == value
        if checked:
            checked = 'checked'
        else:
            checked = None
        option_id = id + u'_' + option_value
        field_parts['input'].append(tag('div',
                tag('input', name=name, value=option_value, id=option_id,
                        checked=checked, type='radio', **attrs),
                tag('label', option_label, for_=option_id),
                        class_=item_css_class))
    error = _render_field_errors(render_kwargs, name)
    add_css_classes = set()
    if error:
        add_css_classes.update(_determine_css_classes(render_kwargs,
                'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(_determine_extra_field_parts(render_kwargs, field_parts, field_extras))
    field_part_list = _determine_field_part_list(render_kwargs, field_parts, field_part_order)
    css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'single_select_list_field', add_css_classes=add_css_classes))
    context.write(tag('div', tag('fieldset', *field_part_list), class_=css_class))
    return ''


@supports_caller
def rename(context, render_kwargs, name=None):
    """
    Read the peppercorn documentation to understand why you need this.
    """
    value = make_start_token(name, RENAME)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    new_render_kwargs = render_kwargs.copy()
    new_render_kwargs['defaults'] = defaults
    new_render_kwargs['errors'] = errors
    new_render_kwargs['getter'] = rename_getter
    if name:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'] + [name]
    else:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'][:]
    closed = render_kwargs.get('closed', False)
    context.write(tag('input', type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(new_render_kwargs)
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def mapping(context, render_kwargs, name=None):
    """
    Wrap a block of fields that should be serialized as a dictionary using
        peppercorn.

    The caller's body should take render_kwargs as an argument.
    """
    value = make_start_token(name, MAPPING)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    new_render_kwargs = render_kwargs.copy()
    new_render_kwargs['defaults'] = defaults
    new_render_kwargs['errors'] = errors
    new_render_kwargs['getter'] = mapping_getter
    if name:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'] + [name]
    closed = render_kwargs.get('closed', False)
    context.write(tag('input', type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(new_render_kwargs)
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def sequence_repeater(context, render_kwargs, name=None, with_adder=False, with_removers=False):
    """
    Output html in a format for repetitions to be added to the sequence on the
    client side.
    
    The caller's body should receive a single argument: render_kwargs.
    """
    value = make_start_token(name, SEQUENCE)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    if name is not None:
        id_stack = render_kwargs['id_stack'] + [name]
    else:
        id_stack = render_kwargs['id_stack'][:]
    closed = render_kwargs.get('closed', False)
    template_render_kwargs = render_kwargs.copy()
    template_render_kwargs['id_stack'] = id_stack + ['__REPEATER__']
    template_render_kwargs['getter'] = sequence_getter
    template_render_kwargs['defaults'] = None
    template_render_kwargs['errors'] = None
    repetition_css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'repetition'))
    template_str = [str(tag('div', class_=repetition_css_class, _closed=False)),
            capture(context, context['caller'].body, template_render_kwargs)]
    if with_removers:
        remover_css_class = _to_css_class(_determine_css_classes(render_kwargs, 'remover'))
        template_str.append(str(tag('input', type_='button', class_=remover_css_class, _closed=closed, value='Remove')))
    template_str.append('</div>')
    template_str = ''.join(template_str)
    repeater_css_class = _to_css_class(_determine_css_classes(render_kwargs, 'repeater'))
    context.write(tag('div', class_=repeater_css_class, _closed=False, **{'data-template': template_str}))
    if hasattr(context['caller'], 'header'):
        context['caller'].header()
    context.write(tag('input', type='hidden', name='__start__', value=value,
            _closed=closed))
    repetitions_css_class = _to_css_class(_determine_css_classes(render_kwargs,
            'repetitions'))
    context.write(tag('div', class_=repetitions_css_class, _closed=False))
    if defaults:
        for index, new_defaults in enumerate(defaults):
            # Errors must be either falsy or contain an entry
            # for every entry in the defaults list, if no error then the
            # entry should be None.
            if errors:
                new_errors = errors[index]
            else:
                new_errors = None
            new_render_kwargs = render_kwargs.copy()
            new_render_kwargs['defaults'] = new_defaults
            new_render_kwargs['errors'] = new_errors
            new_render_kwargs['getter'] = sequence_getter
            new_render_kwargs['id_stack'] = id_stack + [unicode(index)]
            context.write(tag('div', class_=repetition_css_class, _closed=False))
            context['caller'].body(new_render_kwargs)
            if with_removers:
                context.write(tag('input', type_='button', class_=remover_css_class, _closed=closed, value='Remove'))
            context.write('</div>')
            #eof repetition
    context.write('</div>')
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    if with_adder:
        adder_css_class = to_css_class(_determine_css_classes(render_kwargs, 'adder'))
        context.write(tag('input', type_='button', class_=adder_css_class, _closed=closed, value='Add'))
    if hasattr(context['caller'], 'footer'):
        context['caller'].footer()
    context.write('</div>')
    return ''


@supports_caller
def sequence(context, render_kwargs, name=None):
    """
    Wrap a block of fields that should be serialized as a list using
        peppercorn.

    The caller's body should receive a single argument: render_kwargs.
    """
    value = make_start_token(name, SEQUENCE)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    if name is not None:
        id_stack = render_kwargs['id_stack'] + [name]
    else:
        id_stack = render_kwargs['id_stack'][:]
    closed = render_kwargs.get('closed', False)
    context.write(tag('input', type='hidden', name='__start__', value=value,
            _closed=closed))
    if defaults:
        for index, new_defaults in enumerate(defaults):
            # Errors must be either falsy or contain an entry
            # for every entry in the defaults list, if no error then the
            # entry should be None.
            if errors:
                new_errors = errors[index]
            else:
                new_errors = None
            new_render_kwargs = render_kwargs.copy()
            new_render_kwargs['defaults'] = new_defaults
            new_render_kwargs['errors'] = new_errors
            new_render_kwargs['getter'] = sequence_getter
            new_render_kwargs['id_stack'] = id_stack + [unicode(index)]
            context['caller'].body(new_render_kwargs)
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    return ''
