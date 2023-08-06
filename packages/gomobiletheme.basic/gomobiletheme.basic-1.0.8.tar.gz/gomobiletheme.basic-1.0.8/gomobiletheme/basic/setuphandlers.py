
__docformat__ = "epytext"

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3


def runCustomCode(site):
    """ Run custom add-on product installation code to modify Plone site object and others
    
    @param site: Plone site  
    """
    
    if PLONE_VERSION == 3:
    
        # We need to put Plone 3 compatible main_template.pt to the
        # skin stack, 
    
        portal_skins = site.portal_skins
        portal_skins.selections
        
        theme_name = "Go Mobile Default Theme"
        my_theme = portal_skins.selections[theme_name]
        layers = my_theme.split(",")
    
        # Add a new layer between layer "custom" (first) and other layers
        if not "gomobiletheme_plone3" in layers: 
            layers = [ layers[0], "gomobiletheme_plone3" ] + layers[1:] 
        
        # Convert back to string
        layers = ",".join(layers)
        
        # Store the modified skin layer order
        portal_skins.selections[theme_name] = layers
        
        
    
def setupVarious(context):
    """
    @param context: Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('gomobiletheme.basic.marker.txt') is None:
        # Wear
        return

    portal = context.getSite()

    runCustomCode(portal)