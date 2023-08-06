"""
Tools used when rendering the form.

The fields try to be flexible but if you want some heavy modification you are
probably better off just writing your own field and following or faking the
rules of form renderer state.


Field Extras
============

  * What is an example of an ``example`` extra?

    Date Ex: 10-11-1982

  * How would I use ``help`` extra?

    Use JS to roll the help text up and either show it when the input receives
    focus or when the help icon is clicked/hovered.

Field parts and their orders
============================

In order to support re-ordering of the structure of fields you can specify
the order of the parts.  The parts consist of input, label, help, example,
error and a special clear part.  The clear part just inject a div with
a clear class in order to allow floats to be cleared.  This part can occur
more than once in the given order.


Sequences
=========

Usually you want to use a list of dictionaries for this.

If you don't then only one value is available in the body.
"""
from mako.runtime import supports_caller, capture
from webhelpers.misc import NotGiven
from webhelpers.html.tags import select

from pepperedform.renderutils import (sequence_getter, make_start_token,
        _to_css_class, tag)


SEQUENCE = u'sequence'
MAPPING = u'mapping'
RENAME = u'rename'


def primary_form_action(context, state, value, css_classes=None,
        **attrs):
    """
    Primary submit button -- Use this for the main action of the form.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako tempalte.

    ``state``
      A ``FormRendererState`` instance.

    ``value``
      The value for the input tag.

    ``css_classes``
      A set of css classes to add to the css class resolved for this widget.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    attrs['class_'] = _to_css_class(state.determine_css_classes(
            'primary_form_action',
            add_css_classes=css_classes))
    attrs.setdefault('type', 'submit')
    closed = state.is_closed()
    context.write(tag('input', value=value, _closed=closed, **attrs))
    return ''


def secondary_form_action(context, state, value, tag_name='input',
        css_classes=None, **attrs):
    """
    Seconary submit button -- Use this for an action that is less significant
    than the primary action.


    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``value``
      Essentially the name of the action, will be set on the appropriate tag.

    ``tag_name``
      If "input" then an input tag is generated whose value is set to
      ``value``, otherwise a tag with this name is generated and its content
      is filled with the given value.

    ``css_classes``
      A set of css classes to add to the css class resolved for this widget.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    attrs['class_'] = _to_css_class(state.determine_css_classes(
            'secondary_form_action',
            add_css_classes=css_classes))
    if tag_name == 'input':
        attrs.setdefault('type', 'button')
        attrs.setdefault('value', value)
        attrs.setdefault('_closed', state.is_closed())
    else:
        # Content inside the tags.
        attrs.setdefault('c', value)
    context.write(tag(tag_name, **attrs))
    return ''


def hidden_field(context, state, name, value=NotGiven, id=NotGiven,
        field_part_order=None, field_classes=None, **attrs):
    """
    Standard input element of type hidden.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the hidden input tag.

    ``value``
      Optional override of the value attribute resolved by the ``state``.

    ``id``
      Optional override of the id generated from the ``name``.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    if value is NotGiven:
        value = state.field_value(name)
    if id is NotGiven:
        id = state.build_id(name)
    attrs['_closed'] = state.is_closed()
    attrs['class_'] = _to_css_class(state.determine_css_classes(
            'hidden_field'))
    field_parts = {}
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='hidden', **attrs)
    error = state.render_field_errors(name)
    if error:
        field_parts['error'] = error
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    for field_part in field_part_list:
        context.write(field_part)
    return ''


def file_field(context, state, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard input element of type file.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the file input tag.

    ``value``
      Optional override of the value attribute resolved by the ``state``.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    field_parts = {}
    if value is NotGiven:
        value = state.field_value(name)
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    # If the label is None there will be no label.
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    attrs['_closed'] = state.is_closed()
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='file', **attrs)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes('field_has_error'))
        field_parts['error'] = error
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(
            'file_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def password_field(context, state, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard input element of type password.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the input tag.

    ``value``
      Optional override of the value attribute resolved by the ``state``.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    if value is NotGiven:
        value = state.field_value(name)
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    field_parts = {}
    if field_extras:
        _inject_field_extras(field_parts, field_extras)
    attrs['_closed'] = state.is_closed()
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='password', **attrs)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes(
            'field_has_error'))
        field_parts['error'] = error
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(
            'password_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def text_field(context, state, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard input element of type text.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the input tag.

    ``value``
      Optional override of the value attribute resolved by the ``state``.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    if value is NotGiven:
        value = state.field_value(name)
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = state.is_closed()
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('input', name=name, value=value, id=id, type='text', **attrs)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes('field_has_error'))
        field_parts['error'] = error
    css_class = _to_css_class(state.determine_css_classes(
            'text_field', add_css_classes=add_css_classes))
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def checkbox_field(context, state, name, checked=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard input element of type checkbox.

    DO NOT USE THIS FOR A LIST OF CHECKBOXES. THIS IS MEANT FOR A BOOLEAN FIELD.

    If you want to select zero or more of "things" with checkboxes then use
    ``multiple_select_list_field``.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the input tag.

    ``checked``
      True if the checkbox should be checked, otherwise it will not be checked.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the input tag.

    """
    field_type = 'checkbox_field'
    if checked is NotGiven:
        checked = state.field_value(name, False)
    if checked:
        checked = 'checked'
    else:
        checked = None
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = state.is_closed()
    field_parts = {}
    field_parts['input'] = tag('input', name=name, value='1', checked=checked,
            id=id, type='checkbox', **attrs)
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes(
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts,
            field_part_order, field_type=field_type)
    css_class = _to_css_class(state.determine_css_classes(field_type,
            add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def textarea_field(context, state, name, value=NotGiven, id=NotGiven,
        label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard textarea element.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the textarea tag.

    ``value``
      Optional override of the value attribute resolved by the ``state``.

    ``id``
      Optional override of the id attribute generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Override for the ``field_part_order`` determined by the ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the textarea tag.

    """
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    field_type = 'textarea_field'
    if value is NotGiven:
        value = state.field_value(name, u'')
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    field_parts['input'] = tag('textarea', value, name=name, id=id, **attrs)
    error = state.render_field_errors(name)
    if error:
        add_css_classes.update(state.determine_css_classes(
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(field_type,
            add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def single_select_field(context, state, name, options, value=NotGiven,
        id=NotGiven, label=NotGiven, field_extras=None, field_part_order=None,
        field_classes=None, **attrs):
    """
    Standard select element where multiple is not set.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the select tag.

    ``options``
      A list of length 2 tuples where the first entry is the value and the
      second entry is the label. Such as [('1', 'Yes'), ('2', 'No')].

    ``value``
      Optional override of the value resolved by the ``state``. This is matched
      against the first entry of the tuples in the supplied ``options`` to
      determine which option is selected.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Optional override for the ``field_part_order`` determined by the
      ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the select tag.

    """
    if value is NotGiven:
        value = state.field_value(name, NotGiven)
    if value is NotGiven:
        values = []
    else:
        values = [value]
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = state.is_closed()
    field_parts = {}
    field_parts['input'] = select(name, values, options, id=id)
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes(
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(
            'single_select_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def multiple_select_field(context, state, name, options,
        values=NotGiven, id=NotGiven, label=NotGiven, field_extras=None,
        field_part_order=None, field_classes=None, **attrs):
    """
    Standard select element where multiple is set to true.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for the select tag.

    ``options``
      An iterable of length 2 tuples where the first entry is the value and the
      second entry is the label. Such as [('1', 'Yes'), ('2', 'No')].

    ``values``
      Optional override of the values resolved by the ``state``. This is matched
      against the first entry of the tuples in the supplied ``options`` to
      determine which options are selected. This must be an iterable.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Optional override for the ``field_part_order`` determined by the
      ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on the select tag.

    """
    if values is NotGiven:
        values = state.field_value(name, [])
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = state.is_closed()
    field_parts = {}
    if label:
        field_parts['label'] = tag('label', label, for_=id)
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes('field_has_error'))
        field_parts['error'] = error
    field_parts['input'] = select(name, values, options, id=id, multiple=True)
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(
            'multiple_select_field', add_css_classes=add_css_classes))
    context.write(tag('div', *field_part_list, class_=css_class))
    return ''


def multiple_select_list_field(context, state, name, options,
        values=NotGiven, label=NotGiven, id=NotGiven, field_extras=None,
        field_part_order=None, field_classes=None, **attrs):
    """
    Wrap a list of input elements of type checkbox.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for each checkbox.

    ``options``
      An iterable of length 2 tuples where the first entry is the checkbox
      value and the second entry is the checkbox label.
      Such as [('0', 'Bacon'), ('1', 'Eggs'), ('2', 'Toast')].

    ``values``
      Optional override of the values resolved by the ``state``. The values are
      used to determine which options are selected. This must be an
      iterable.

    ``label``
      Optional override of the label generated from the ``name``.

    ``id``
      Optional override of the id generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.

    ``field_part_order``
      Optional override for the ``field_part_order`` determined by the
      ``state``.

    ``**attrs``
      All remaining kwargs are set as attributes on each checkbox input tag.

    """
    if values is NotGiven:
        values = state.field_value(name, [])
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    closed = state.is_closed()
    attrs['_closed'] = closed
    start_token = make_start_token(name, SEQUENCE)
    field_parts = {}
    # Start list now because peppercorn stuff must always wrap around the
    # field parts.
    field_part_list = []
    field_part_list.append(tag('input', type='hidden', name='__start__', value=start_token, _closed=closed))
    if label:
        field_parts['label'] = tag('legend', label)
    item_css_class = _to_css_class(state.determine_css_classes(
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
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes(
            'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list.extend(state.determine_field_part_list(field_parts, field_part_order))
    field_part_list.append(tag('input', type='hidden', name='__end__',
            value=start_token, _closed=closed))
    css_class = _to_css_class(state.determine_css_classes(
            'multiple_select_list_field', add_css_classes=add_css_classes))
    context.write(tag('div', tag('fieldset', *field_part_list), class_=css_class))
    return ''


def single_select_list_field(context, state, name, options,
        value=NotGiven, id=NotGiven, label=NotGiven, field_extras=None,
        field_part_order=None, field_classes=None, **attrs):
    """
    Wrap a list of input elements of type radio.

    ``context``
      A mako context, this won't be needed if this module is used as a
      namespace in a mako template.

    ``state``
      A ``FormRendererState`` instance.

    ``name``
      The name attribute for each radio.

    ``options``
      An iterable of length 2 tuples where the first entry is the value and the
      second entry is the label.
      Such as [('0', 'Red'), ('1', 'Green'), ('2', 'Blue')].

    ``value``
      Optional override of the value resolved by the ``state``. The value is
      used to determine which option is selected.

    ``id``
      Optional override of the id generated from the ``name``.

    ``label``
      Optional override of the label generated from the ``name``.

    ``field_extras``
      Optional dictionary mapping a field extra by name to content.  This must
      be set if you wish to use field extras.  See this module docstring for
      more information.  This applies to this field as a whole and not to
      individual inputs.

    ``field_part_order``
      Optional override for the ``field_part_order`` determined by the
      ``state``.

    ``field_classes``
      A iterable of css classes to add to the css class resolved for this field.

    ``**attrs``
      All remaining kwargs are set as attributes on each radio input tag.

    """
    if value is NotGiven:
        value = state.field_value(name)
    if id is NotGiven:
        id = state.build_id(name)
    if label is NotGiven:
        label = name.replace(u'_', u' ').title()
    attrs['_closed'] = state.is_closed()
    field_parts = {}
    if label:
        field_parts['label'] = tag('legend', label)
    item_css_class = _to_css_class(state.determine_css_classes(
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
    error = state.render_field_errors(name)
    if field_classes:
        add_css_classes = set(field_classes)
    else:
        add_css_classes = set()
    if error:
        add_css_classes.update(state.determine_css_classes(
                'field_has_error'))
        field_parts['error'] = error
    if field_extras:
        field_parts.update(state.determine_extra_field_parts(field_parts, field_extras))
    field_part_list = state.determine_field_part_list(field_parts, field_part_order)
    css_class = _to_css_class(state.determine_css_classes(
            'single_select_list_field', add_css_classes=add_css_classes))
    context.write(tag('div', tag('fieldset', *field_part_list), class_=css_class))
    return ''


@supports_caller
def rename(context, state, name=None):
    """
    Read the peppercorn documentation to understand why you need this.
    """
    closed = state.is_closed()
    value = make_start_token(name, RENAME)
    context.write(tag('input', type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(state.rename_descend(name))
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def mapping(context, state, name=None):
    """
    Wrap a block of fields that should be serialized as a dictionary using
        peppercorn.

    The caller's body should take state as an argument.
    """
    closed = state.is_closed()
    value = make_start_token(name, MAPPING)
    context.write(tag('input', type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(state.mapping_descend(name))
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def sequence_repeater(context, state, name=None, with_adder=False, with_removers=False):
    """
    Output html in a format for repetitions to be added to the sequence on the
    client side.

    The caller's body should receive a single argument: state.
    """
    closed = state.is_closed()
    repetition_css_class = _to_css_class(state.determine_css_classes('repetition'))
    #
    # Construct the repeater template and shove it into a div as a data
    # attribute.
    #
    template_state = state.clone(defaults=None, errors=None,
        id_stack=state.push_id_stack(name, '__REPEATER__'),
        getter=sequence_getter)
    template_str = [str(tag('div', class_=repetition_css_class, _closed=False)),
            capture(context, context['caller'].body, template_state)]
    if with_removers:
        remover_css_class = _to_css_class(state.determine_css_classes('remover'))
        template_str.append(str(tag('input', type_='button', class_=remover_css_class, _closed=closed, value='Remove')))
    template_str.append('</div>')
    template_str = ''.join(template_str)
    repeater_css_class = _to_css_class(state.determine_css_classes('repeater'))
    context.write(tag('div', class_=repeater_css_class, _closed=False, **{'data-template': template_str}))
    #
    # Optionally include a header.
    #
    if hasattr(context['caller'], 'header'):
        context['caller'].header()
    #
    # Loop, rendering each repetition and optionally a remove button.
    #
    value = make_start_token(name, SEQUENCE)
    context.write(tag('input', type='hidden', name='__start__', value=value,
            _closed=closed))
    repetitions_css_class = _to_css_class(state.determine_css_classes('repetitions'))
    # Wrap all the repetitions in another div.
    context.write(tag('div', class_=repetitions_css_class, _closed=False))
    for new_state in state.sequence_descend(name):
        # Wrap each repetition in a div.
        context.write(tag('div', class_=repetition_css_class, _closed=False))
        context['caller'].body(new_state)
        if with_removers:
            context.write(tag('input', type_='button', class_=remover_css_class, _closed=closed, value='Remove'))
        context.write('</div>')
    context.write('</div>')
    context.write(tag('input', type='hidden', name='__end__', value=value, _closed=closed))
    #
    # Optionally include an add button.
    #
    if with_adder:
        adder_css_class = _to_css_class(state.determine_css_classes('adder'))
        context.write(tag('input', type_='button', class_=adder_css_class, _closed=closed, value='Add'))
    #
    # Optionally include a footer.
    #
    if hasattr(context['caller'], 'footer'):
        context['caller'].footer()
    context.write('</div>')
    return ''


@supports_caller
def sequence(context, state, name=None):
    """
    Wrap a block of fields that should be serialized as a list using
        peppercorn.

    The caller's body should receive a single argument: state.

    This function kicks abstraction right in the face.
    """
    closed = state.is_closed()
    value = make_start_token(name, SEQUENCE)
    context.write(tag('input', type='hidden', name='__start__', value=value,
            _closed=closed))
    for new_state in state.sequence_descend(name):
        context['caller'].body(new_state)
    context.write(tag('input', type='hidden', name='__end__', value=value,
            _closed=closed))
    return ''
