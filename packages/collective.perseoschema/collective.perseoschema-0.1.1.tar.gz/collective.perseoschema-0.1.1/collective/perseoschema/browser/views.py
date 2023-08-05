from collective.perseo.browser.views import PerSEOTabContext
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    
class PerSEOTabContextSchemaOrg( PerSEOTabContext ):
    """ This class contains methods that allows to manage SEO tab.
    """
    template = ViewPageTemplateFile('templates/perseo_tab_context.pt')
