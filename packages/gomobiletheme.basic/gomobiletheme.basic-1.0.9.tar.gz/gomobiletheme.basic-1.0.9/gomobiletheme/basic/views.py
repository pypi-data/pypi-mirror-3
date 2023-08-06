"""

    Override some Plone out-of-the-box contente views to  be more mobile friendly.

"""

from five import grok

from interfaces import IThemeLayer

# Use templates directory to search for templates.
grok.templatedir('templates')

# Viewlets are active only when gomobiletheme.basic theme layer is activated
grok.layer(IThemeLayer)

from Products.ATContentTypes.interface import IATFolder
class MobileFolderDefault(grok.View):
    """ A page renderer.

    Render Page content for anonymous visitors.
    """
    grok.context(IATFolder)
    grok.require('zope2.View')
    grok.template("folder")


from Products.ATContentTypes.interface import IATDocument
class MobileDocumentDefault(grok.View):
    """ A page renderer.

    Render Page content for anonymous visitors.
    """
    grok.context(IATDocument)
    grok.require('zope2.View')
    grok.template("document")


