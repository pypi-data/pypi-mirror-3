from django.utils.encoding import force_unicode

from markupmirror.exceptions import *


class BaseMarkup(object):
    """Basic interface for markup converter classes.

    An example converter could look like this::

        class ExampleMarkup(BaseMarkup):

            def convert(self, markup):
                return markup.replace("example", "markup")

    """
    codemirror_mode = ''
    title = ""

    @classmethod
    def get_name(cls):
        """Returns lowercase markup name, without the "Markup" part.

        Class naming convention is ``<Markup-Type>Markup``.
        """
        return cls.__name__.replace("Markup", "", 1).lower()

    def convert(self, markup):
        """Main conversion method. Must be implemented in subclasses."""
        return markup

    def before_convert(self, markup):
        """Called before ``convert``. Can be used to separate the main
        conversion through a third-party library (e.g. Markdown) from
        additional logic.

        """
        return markup

    def after_convert(self, markup):
        """Called after ``convert``. Similar to ``before_convert``."""
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

        Alternatively you can also use the ``del`` operator::

           del markup_pool['restructuredtext']

        """
        if markup_name in self.markups:
            del self.markups[markup_name]

    def has_markup(self, markup_name):
        """Tests if a markup converter with the name ``markup_name`` is already
        registered with the markup pool.

        Alternatively you can also use the ``in`` operator, like with a
        dictionary::

            if 'restructuredtext' in markup_pool:
                pass

        """
        return markup_name in self.markups

    def get_markup(self, markup_name):
        """Returns one markup converter by name.
        Raises ``KeyError`` if no converter was registered by ``markup_name``.

        Alternatively you can also use the ``[]`` accessor, like with a
        dictionary::

            markup = markup_pool['restructuredtext']

        """
        return self.markups[markup_name]

    def __contains__(self, key):
        return self.has_markup(key)

    def __getitem__(self, key):
        return self.get_markup(key)

    def __delitem__(self, key):
        self.unregister_markup(key)


markup_pool = MarkupPool()  # Instance of ``MarkupPool`` for public use.
register_markup = markup_pool.register_markup


__all__ = ('markup_pool', 'register_markup', 'BaseMarkup')
