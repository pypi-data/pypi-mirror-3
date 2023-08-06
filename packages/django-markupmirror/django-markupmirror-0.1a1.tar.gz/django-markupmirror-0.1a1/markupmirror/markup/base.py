from django.utils.encoding import force_unicode

from markupmirror.exceptions import *


class BaseMarkup(object):
    """Basic interface for markup converter classes.

    """
    codemirror_mode = ''
    title = ""

    @classmethod
    def get_name(cls):
        """Returns lowercase markup name, without the "Markup" part."""
        return cls.__name__.replace("Markup", "", 1).lower()

    def before_convert(self, markup):
        """Called before ``convert``."""
        return markup

    def after_convert(self, markup):
        """``Called after ``convert``."""
        return markup

    def convert(self, markup):
        """Main conversion method. Use third-pary libraries here."""
        return markup

    def __call__(self, markup):
        """Main entry point. Calls ``before_convert``, ``convert`` and
        ``after_convert`` in that order.

        """
        return force_unicode(
            self.after_convert(self.convert(self.before_convert(markup))))


class MarkupPool(object):
    """Pool for markup converters.

    Each markup class, subclassing
    ``markupmirror.markup.base.BaseMarkup``, must register to this
    pool using ``register_markup`` defined below.

    """
    def __init__(self):
        self.markups = {}

    def register_markup(self, markup):
        """Registers a markup converter class.

        ``markup`` must be a subclass of ``BaseMarkup`` and may not be
        registered already.

        """
        # check for correct subclassing
        if not issubclass(markup, BaseMarkup):
            raise InvalidMarkup(
                "Markups must be subclasses of "
                "markupmirror.markup.base.BaseMarkup. %r is not."
                % markup)

        markup_name = markup.get_name()
        self.markups[markup_name] = markup()

    def unregister_markup(self, markup_name):
        """Unregisters a markup converter with the name ``markup_name``.
        Fails silently if no converter was registered by that name.
        """
        if markup_name in self.markups:
            del self.markups[markup_name]

    def has_markup(self, name):
        return name in self.markups

    def get_markup(self, name):
        """Returns one markup converter by name.
        Raises ``KeyError`` if no converter was registered by ``name``.

        """
        return self.markups[name]

    def __contains__(self, key):
        return self.has_markup(key)

    def __getitem__(self, key):
        return self.get_markup(key)

    def __delitem__(self, key):
        self.unregister_markup(key)


markup_pool = MarkupPool()
register_markup = markup_pool.register_markup


__all__ = ('markup_pool', 'register_markup', 'BaseMarkup')
