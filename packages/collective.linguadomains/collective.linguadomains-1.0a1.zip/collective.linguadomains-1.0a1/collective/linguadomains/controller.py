from urlparse import urlparse
from zope import component
from zope import interface
from plone.registry.interfaces import IRegistry
from collective.linguadomains.controlpanel import ISettingsSchema

import logging
logger = logging.getLogger('collective.linguadomains')

class ILinguaDomainsManager(interface.Interface):
    """Controller interface"""
    
    def validate_urls(mapping=None, urls=None):
        """This method return True if provided URL exists.
        You can check by providing the mapping or a list of URL"""

    def set_mapping(mapping):
        """Save the mapping"""

    def get_mapping():
        """return current mapping"""

    def language():
        """return current context language"""

    def get_translated_url():
        """Return the translated url. if already translate, return it"""

class LinguaDomainsManager(object):
    """Controller to check if domain name is translated and valide according
    to language"""

    interface.implements(ILinguaDomainsManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._settings = None
        self._portal_url = None

    def _plone_portal_state(self):
        return component.queryMultiAdapter((self.context, self.request),
                                           name="plone_portal_state")

    def portal_url(self):
        if self._portal_url is None:
            pstate = self._plone_portal_state()
            self._portal_url = pstate.portal_url()
        return self._portal_url

    def language(self):
        return self.context.Language()

    def settings(self):
        if self._settings is None:
            registry = component.queryUtility(IRegistry)
            if registry is None:
                logger.info('no registry')
                return
        
            self._settings = registry.forInterface(ISettingsSchema,
                                                    check=False)
        return self._settings

    def get_mapping(self):
        settings = self.settings()

        if not settings:
            return

        if not settings.activated:
            return

        mapping_raw = settings.mapping
        mapping = {}
        for value in mapping_raw:
            url , langcode = value.split('|')
            mapping[langcode] = url

        return mapping

    def get_translated_url(self):

        url = self.request.get('ACTUAL_URL')
        purl = self.portal_url()
        lang = self.language()

        mapping = self.get_mapping()

        if not mapping:
            return url

        if not purl in mapping.values():
            logger.info('URL not configured')
            return url

        waited_url = mapping.get(lang,None)
        if waited_url is None:
            logger.info('Language not configured')
            return url
        waited_url_parsed = urlparse(waited_url)

        if purl  == waited_url:
            return url

        purl_parsed = urlparse(purl)
        url_parsed = urlparse(url)

        base_path = purl_parsed.path
        waited_path = url_parsed.path
        redirect_url = waited_url + waited_path[len(base_path):]
    
        return redirect_url
