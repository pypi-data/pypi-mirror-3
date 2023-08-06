from django.conf import settings


# Default markup type
# Used for fields which have no markup_type or default_markup_type assigned
# before a markup_type has been selected by the user (selectbox).
DEFAULT_MARKUP_TYPE = getattr(settings,
    'MARKUPMIRROR_DEFAULT_MARKUP_TYPE', 'plaintext')


# CodeMirror settings

# Minified JS and CSS files
MARKUPMIRROR_JS = (
    'markupmirror/jquery-1.7.2.min.js',
    'markupmirror/codemirror.min.js',
    'markupmirror/markupmirror.js',
)
MARKUPMIRROR_CSS = (
    'markupmirror/codemirror.min.css',
    'markupmirror/markupmirror.css',
)


# Settings for markup converters

# Extensions and settings for markdown
MARKDOWN_EXTENSIONS = getattr(settings,
    'MARKUPMIRROR_MARKDOWN_EXTENSIONS',
    ['extra', 'headerid(level=2)'])
MARKDOWN_OUTPUT_FORMAT = getattr(settings,
    'MARKUPMIRROR_MARKDOWN_OUTPUT_FORMAT',
    'html5')

# Filter settings for reStructuredText
RESTRUCTUREDTEXT_FILTER = getattr(settings,
    'MARKUPMIRROR_RESTRUCTUREDTEXT_FILTER',
    {})

# Textile settings
TEXTILE_SETTINGS = getattr(settings,
    'MARKUPMIRROR_TEXTILE_SETTINGS',
    {'encoding': 'utf-8', 'output': 'utf-8'})


# Settings for MarkupMirrorContent for FeinCMS

# Init template for CodeMirror in FeinCMS
FEINCMS_INIT_TEMPLATE = getattr(settings,
    'MARKUPMIRROR_FEINCMS_INIT_TEMPLATE',
    'admin/markupmirror/feincms/init_codemirror.html')

# Context for init template
FEINCMS_INIT_CONTEXT = getattr(settings,
    'MARKUPMIRROR_FEINCMS_INIT_CONTEXT', {
    #     'CODEMIRROR_JS': CODEMIRROR_JS,
    #     'CODEMIRROR_CSS': CODEMIRROR_CSS,
        'CODEMIRROR_PATH': settings.STATIC_URL + 'markupmirror/',
        'CODEMIRROR_WIDTH': '50%',
        'CODEMIRROR_HEIGHT': '300px',
    })
