try:
    import feincms
except ImportError:
    raise ImportError(
        "FeinCMS is required to use markupmirror.feincms.MarkupMirrorContent.")
