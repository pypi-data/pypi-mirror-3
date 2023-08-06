from plone.theme.interfaces import IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Experimental Radial (Pie) Menu for time input" theme, this interface must be its layer
       (in pietimemenu/viewlets/configure.zcml).
    """
