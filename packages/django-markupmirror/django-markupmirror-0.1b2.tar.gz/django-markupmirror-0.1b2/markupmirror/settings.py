from django.conf import settings


# Default markup type
# Used for fields which have no markup_type or default_markup_type assigned
# before a markup_type has been selected by the user (selectbox).
MARKUPMIRROR_DEFAULT_MARKUP_TYPE = getattr(settings,
    'MARKUPMIRROR_DEFAULT_MARKUP_TYPE', 'plaintext')


# CodeMirror settings

# Minified JS and CSS files
MARKUPMIRROR_JS = (
    'markupmirror/jquery-1.7.2.min.js',
    'markupmirror/jquery.cookie.min.js',
    'markupmirror/codemirror.min.js',
    'markupmirror/markupmirror.js',
)
MARKUPMIRROR_CSS = (
    'markupmirror/codemirror.min.css',
    'markupmirror/markupmirror.css',
)


# Settings for markup converters

# Extensions and settings for markdown
MARKUPMIRROR_MARKDOWN_EXTENSIONS = getattr(settings,
    'MARKUPMIRROR_MARKDOWN_EXTENSIONS',
    ['extra', 'headerid(level=2)'])

MARKUPMIRROR_MARKDOWN_OUTPUT_FORMAT = getattr(settings,
    'MARKUPMIRROR_MARKDOWN_OUTPUT_FORMAT',
    'html5')


# Textile settings
MARKUPMIRROR_TEXTILE_SETTINGS = getattr(settings,
    'MARKUPMIRROR_TEXTILE_SETTINGS',
    {'encoding': 'utf-8', 'output': 'utf-8'})


# CodeMirror settings

MARKUPMIRROR_CODEMIRROR_SETTINGS = getattr(settings,
    'MARKUPMIRROR_CODEMIRROR_SETTINGS', {
        'width': '50%',
        'height': '300px',
        'indentUnit': 4,
        'lineNumbers': True,
        'lineWrapping': True,
        'path': settings.STATIC_URL + 'markupmirror/',
    })
