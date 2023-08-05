from collective.perseo.browser.seo_config import PerSEOConfig, \
schemaorgset, wmtoolsset, titleset, indexingset, sitemapxmlset, rssset
from plone.fieldsets.fieldsets import FormFieldsets

class PerSEOConfigSchemaOrg(PerSEOConfig):
    """"""
    form_fields = FormFieldsets(wmtoolsset, titleset, indexingset,
                                sitemapxmlset, schemaorgset, rssset)
