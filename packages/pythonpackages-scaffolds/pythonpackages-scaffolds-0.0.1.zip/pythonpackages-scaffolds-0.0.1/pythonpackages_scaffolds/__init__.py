from zopeskel.basic_namespace import BasicNamespace


class PloneTheme(BasicNamespace):
    """
    Template class that requires a namespace package and
    uses the templates in the plone_theme directory.
    """
    _template_dir = 'plone_theme'
    summary = 'Diazo theme for Plone 4'
