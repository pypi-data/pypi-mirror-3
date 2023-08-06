"""
Non-mako utility functions used during rendering.
"""
from types import StringTypes
from webhelpers.misc import NotGiven
from webhelpers.html.builder import HTML


tag = HTML.tag
" Shorthand for webhelpers tag generator. "


default_field_part_orders = {
    'checkbox_field': ('input', 'label', 'help', 'example', 'error'),
    None: ('label', 'help', 'example', 'input', 'error')
}
"""
Map from field type to list of field part names.
The None key designates the default order since not all field types will have an entry.

Overwrite these in the render_kwargs.
"""


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


def sequence_getter(items, name, if_missing=None):
    """ A sequence should pass this function to its children to get their
    defaults or errors.

    @NOTE: The name here is ignored.
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


def render_example(css_class, example):
    if type(example) not in (list, tuple):
        example = [example]
    return tag('span', *example, class_=css_class)


def render_help(css_class, help_):
    return tag('span', field_extras['help'], class_=css_class)


default_extra_renderers = {
    'example': render_example,
    'help': render_help,

}


class FormRenderer(object):
    """
    Use this to encapsulate configured across multiple renderings.
    """
    def __init__(self, css_classes=default_css_classes,
            extra_renderers=default_extra_renderers,
            field_part_orders=default_field_part_orders, closed=False):
        """
        ``css_classess``
          A dictionary containing css classes as either strings or sets which
          are mapped by special keys referenced by the functions in
          :module:``pepperedform.render``.  See ``default_css_classes`` for
          a list of the signifigant keys.

        ``extra_renderers``
          A dictionary containing functions for renderer extra parts of fields.
          These parts must be referenced in the ``field_part_orders`` in order
          to be renderer with the same key as their renderer.  Only ``example``
          and ``help`` are supported right now.

          ``field_part_orders``
          A dictionary mapping each field type to a list of field part keys
          that are used to determine in what order to render the parts of that
          type of field.  The ``None`` entry is used as the default field part
          order. For example if the label should occur before or after the
          input.  See ``default_field_part_orders`` for the supported list of
          field parts.

          ``closed``
          Close inputs for xhtml(4/5) or do not close them for regular
          html(4/5).  Nothing genius here.
        """

        self.css_classes = css_classes
        self.extra_renderers = extra_renderers
        self.closed = closed
        self.field_part_orders = field_part_orders

    def form_renderer_state(self, defaults, errors):
        return FormRendererState(self, defaults, errors, [], mapping_getter)


class FormRendererState(object):
    """
    This class encapsulates state for an intitial rendering but also for nested
    renderings.
    """
    def __init__(self, renderer, defaults, errors, id_stack, getter):
        self.renderer = renderer
        self.defaults = defaults
        self.errors = errors
        self.id_stack = id_stack
        self.getter = getter

    def is_closed(self):
        return self.renderer.closed


    def clone(self, renderer=NotGiven, defaults=NotGiven, errors=NotGiven,
            id_stack=NotGiven, getter=NotGiven):
        if renderer is NotGiven:
            renderer = self.renderer
        if defaults is NotGiven:
            defaults = self.defaults
        if errors is NotGiven:
            errors = self.errors
        if id_stack is NotGiven:
            id_stack = self.id_stack
        if getter is NotGiven:
            getter = self.getter
        return FormRendererState(renderer, defaults, errors, id_stack, getter)

    def rename_descend(self, name):
        defaults = self.field_value(name)
        errors = self.field_error(name)
        id_stack = self.push_id_stack(name)
        return FormRendererState(self.renderer, defaults, errors, id_stack,
                sequence_getter)

    def mapping_descend(self, name):
        defaults = self.field_value(name)
        errors = self.field_error(name)
        id_stack = self.push_id_stack(name)
        return FormRendererState(self.renderer, defaults, errors, id_stack,
                mapping_getter)

    def sequence_descend(self, name, getter=mapping_getter):
        defaults = self.field_value(name)
        errors = self.field_error(name)
        id_stack = self.push_id_stack(name)
        if defaults:
            for index, new_defaults in enumerate(defaults):
                # Errors must be either falsy or contain an entry
                # for every entry in the defaults list, if no error then the
                # entry should be None.
                if errors:
                    new_errors = errors[index]
                else:
                    new_errors = None
                new_id_stack = id_stack + [unicode(index)]
                yield FormRendererState(self.renderer, new_defaults,
                        new_errors, new_id_stack, sequence_getter)

    def determine_css_classes(self, class_name,
                add_css_classes=None):
        """
        Determine the css classes to use by first checking the dict at the
            `css_classes` key in render_kwargs and then checking defaults in this
            module.
        """
        css_classes = self.renderer.css_classes[class_name]
        # Wart to handle css classes as a string.
        if isinstance(css_classes, StringTypes):
            css_classes = set([css_classes])
        # Wart to handle css classes as a list or tuple.
        elif not isinstance(css_classes, set):
            css_classes = set(css_classes)
        if add_css_classes:
            css_classes.update(add_css_classes)
        return css_classes

    def determine_field_part_list(self, field_parts, field_part_order, field_type=None):
        """
        Determine the order of the parts, such as label and input, in the HTML.

        Note: This can be overridden in the render_kwargs by the field_type in a
            dict at the `field_part_orders` key, use the field_type `None` to match
            all unmatched field types. If no field part order is found in the
            dict in render kwargs then defaults in this module are used.

        A special field part exists to to inject a clearing div.
        """
        if not field_part_order:
            if field_type:
                field_part_order = self.renderer.field_part_orders.get(field_type, None)
            if not field_part_order:
                field_part_order = self.renderer.field_part_orders.get(None, None)
        if not field_part_order:
            # @TODO: Should we raise a warning here?
            field_part_order = []
        field_part_list = []
        for field_part_name in field_part_order:
            # Hack in order to clear floats.
            if field_part_name == 'clear':
                clear_class = self.determine_clear_class('clear')
                field_part_list.append(tag('div', '', class_=clear_class, _closed=True))
            elif field_part_name in field_parts:
                # Flatten iterable field parts into the existing list.
                if type(field_parts[field_part_name]) in (list, tuple):
                    field_part_list.extend(field_parts[field_part_name])
                else:
                    field_part_list.append(field_parts[field_part_name])
        return field_part_list

    def field_value(self, name, if_missing=None):
        return self.getter(self.defaults, name, if_missing=if_missing)

    def field_error(self, name, if_missing=None):
        return self.getter(self.errors, name, if_missing=if_missing)

    def push_id_stack(self, *names):
        return self.id_stack + [name for name in names if name]

    def build_id(self, *names):
        return u'_'.join(self.push_id_stack(*names))

    def render_field_errors(self, name):
        """
        Return an error messages div or None, each error is wrapped in a span.
        """
        errors = self.field_error(name)
        error_div = None
        if errors:
            error_spans = []
            if type(errors) in (list, tuple):
                for error in errors:
                    error_spans.append(tag('span', error))
            else:
                error_spans.append(tag('span', errors))
            css_class = _to_css_class(self.determine_css_classes('field_errors'))
            error_div = tag('div', *error_spans, class_=css_class)
        return error_div

    def determine_extra_renderer(self, extra_name):
        return self.renderer.extra_renderers.get(extra_name, None)

    def determine_extra_field_parts(self, field_parts, field_extras):
        """
        Build any extra field parts as necessary, such as an example or help.
        """
        extra_field_parts = {}
        if field_extras and 'example' in field_extras:
            render_example = self.determine_extra_renderer('example')
            if render_example:
                example_css_class = _to_css_class(
                    self.determine_css_classes('field_example'))
                extra_field_parts['example'] = render_example(
                        css_class=example_css_class,
                        example=field_extras['example'])
        if field_extras and 'help' in field_extras:
            render_help = self.determine_extra_renderer('help')
            if render_help:
                help_css_class = _to_css_class(self.determine_css_classes(
                        'field_help'))
                extra_field_parts['help'] = render_help(class_=help_css_class,
                        help_=field_extras['help'])
        return extra_field_parts


def _to_css_class(css_classes):
    return ' '.join(css_classes)
