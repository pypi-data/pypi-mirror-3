from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe

from markupmirror import widgets
from markupmirror.markup.base import markup_pool


# suffixes for rendered and markup_type fields
_rendered_field_name = lambda name: '%s_rendered' % name
_markup_type_field_name = lambda name: '%s_markup_type' % name


class Markup(object):
    """Wrapper class for markup content output.

    Stores the names of the associated field, the rendered field and the
    markup_type field to make assignment possible.

    When accessing the value of a ``MarkupField``, a ``Markup`` instance will
    be returned. This provides a few methods to access the raw and rendered
    markup, and the markup type of the saved content.

    """
    def __init__(self, instance, field_name,
                 rendered_field_name, markup_type_field_name):
        self.instance = instance
        self.field_name = field_name
        self.rendered_field_name = rendered_field_name
        self.markup_type_field_name = markup_type_field_name

    @property
    def raw(self):
        """The raw markup content."""
        return self.instance.__dict__[self.field_name]

    @raw.setter
    def raw(self, value):
        return setattr(self.instance, self.field_name, value)

    @property
    def markup_type(self):
        """Markup type of the current markup content."""
        return self.instance.__dict__[self.markup_type_field_name]

    @markup_type.setter
    def markup_type(self, value):
        return setattr(self.instance, self.markup_type_field_name, value)

    @property
    def rendered(self):
        """Returns the rendered markup content (read only). This is only
        available after ``Model.save`` has been called.

        """
        return getattr(self.instance, self.rendered_field_name)

    def __unicode__(self):
        """Allows display via templates to work without safe filter. Same as
        ``rendered``.

        """
        return mark_safe(self.rendered)


class MarkupMirrorFieldDescriptor(object):
    """Descriptor class for field functionality."""

    def __init__(self, field):
        self.field = field
        self.rendered_field_name = _rendered_field_name(self.field.name)
        self.markup_type_field_name = _markup_type_field_name(self.field.name)

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("Can only be accessed via an instance.")
        markup = instance.__dict__[self.field.name]
        if markup is None:
            return None
        return Markup(instance, self.field.name,
                      self.rendered_field_name, self.markup_type_field_name)

    def __set__(self, obj, value):
        if isinstance(value, Markup):
            obj.__dict__[self.field.name] = value.raw
            setattr(obj, self.rendered_field_name, value.rendered)
            setattr(obj, self.markup_type_field_name, value.markup_type)
        else:
            obj.__dict__[self.field.name] = value


class MarkupMirrorField(models.TextField):
    """Field to store markup content.

    The ``MarkupMirrorField`` adds three fields to the model it is used in.

    * One field for the raw markup content (``<field_name>``).
    * One field for the rendered HTML content (``<field_name>_rendered``).
    * One field that specifies the markup type (``<field_name>_markup_type``).

    The field can be used with a fixed ``markup_type`` or a
    ``default_markup_type``, which displays an additional selection widget
    for the available markup types. However, only one of ``markup_type`` and
    ``default_markup_type`` can be provided.

    If neither is provided, the setting ``MARKUPMIRROR_DEFAULT_MARKUP_TYPE``
    is used as ``default_markup_type`` instead.

    """
    def __init__(self, verbose_name=None, name=None,
                 markup_type=None, default_markup_type=None,
                 escape_html=False, **kwargs):
        if markup_type and default_markup_type:
            raise ImproperlyConfigured(
                "Cannot specify both markup_type and default_markup_type")

        self.default_markup_type = markup_type or default_markup_type
        self.markup_type_editable = markup_type is None
        self.escape_html = escape_html

        if (self.default_markup_type and
            self.default_markup_type not in markup_pool):
            raise ImproperlyConfigured(
                "Invalid default_markup_type for field '%r', "
                "available types: %s" % (
                    name or verbose_name,
                    ', '.join(sorted(markup_pool.markups.keys()))))

        # for South FakeORM compatibility: the frozen version of a
        # MarkupMirrorField can't try to add a _rendered field, because the
        # _rendered field itself is frozen as well. See introspection
        # rules below.
        self.rendered_field = not kwargs.pop('rendered_field', False)

        super(MarkupMirrorField, self).__init__(verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        """Adds two additional fields for rendered HTML content and markup type
        to the model.

        """
        if not cls._meta.abstract:
            # markup_type
            choices = [(markup_type, markup.title) for markup_type, markup in
                sorted(markup_pool.markups.iteritems(),
                    key=lambda markup: markup[1].title.lower())]
            markup_type_field = models.CharField(
                choices=choices, max_length=30,
                default=self.default_markup_type, blank=self.blank,
                editable=self.markup_type_editable)
            markup_type_field.creation_counter = self.creation_counter + 1

            # rendered
            rendered_field = models.TextField(
                editable=False, blank=True, null=True)
            rendered_field.creation_counter = self.creation_counter + 2

            # add fields to class
            cls.add_to_class(_markup_type_field_name(name), markup_type_field)
            cls.add_to_class(_rendered_field_name(name), rendered_field)

        super(MarkupMirrorField, self).contribute_to_class(cls, name)

        # use MarkupMirrorFieldDescriptor to access this field
        setattr(cls, self.name, MarkupMirrorFieldDescriptor(self))

    def pre_save(self, model_instance, add):
        value = super(MarkupMirrorField, self).pre_save(model_instance, add)

        # check for valid markup type
        if value.markup_type not in markup_pool:
            raise ValueError(
                'Invalid markup type (%s), available types: %s' % (
                    value.markup_type,
                    ', '.join(sorted(markup_pool.markups.keys()))))

        # escape HTML
        if self.escape_html:
            raw = escape(value.raw)
        else:
            raw = value.raw

        rendered = markup_pool[value.markup_type](raw)
        setattr(model_instance, _rendered_field_name(self.attname), rendered)
        return value.raw

    def get_prep_value(self, value):
        if isinstance(value, Markup):
            return value.raw
        else:
            return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.raw

    def formfield(self, **kwargs):
        """Adds attributes necessary for CodeMirror initialization to the
        field's widget.

        The class "item-markupmirror" is used to identify textareas that should
        be enhanced with the editor.

        The ``data-mode`` and ``data-markuptype`` attributes depend on a
        selected ``default_markup_type``. If a field does not have a default
        markup type selected, the attributes will be added in the widgets'
        ``render`` method by accessing the ``markup_type`` property of the
        markup content wrapper ``markupmirror.fields.Markup``.

        """
        widget_attrs = {
            'class': 'item-markupmirror',
        }
        if (self.default_markup_type and
            self.default_markup_type in markup_pool):
            widget_attrs['data-mode'] = markup_pool[
                self.default_markup_type].codemirror_mode
            widget_attrs['data-markuptype'] = self.default_markup_type

        defaults = {
            'widget': widgets.MarkupMirrorTextarea(attrs=widget_attrs),
        }

        defaults.update(kwargs)
        return super(MarkupMirrorField, self).formfield(**defaults)


__all__ = ('Markup', 'MarkupMirrorFieldDescriptor', 'MarkupMirrorField')


# register MarkupMirrorField to use the custom widget in the Admin
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS

FORMFIELD_FOR_DBFIELD_DEFAULTS[MarkupMirrorField] = {
    'widget': widgets.AdminMarkupMirrorTextareaWidget,
}


# allow South to handle MarkupMirrorField smoothly
try:
    from south.modelsinspector import add_introspection_rules
    # For a normal MarkupMirrorField, the add_rendered_field attribute is
    # always True, which means no_rendered_field arg will always be
    # True in a frozen MarkupMirrorField, which is what we want.
    add_introspection_rules(
        rules=[
            ((MarkupMirrorField,), [], {
                'rendered_field': ['rendered_field', {}],
            })
        ],
        patterns=['markupmirror\.fields\.MarkupMirrorField'])
except ImportError:
    pass
