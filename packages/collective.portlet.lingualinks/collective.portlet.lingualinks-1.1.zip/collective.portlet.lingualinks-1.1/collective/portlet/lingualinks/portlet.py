from Acquisition import aq_inner
from zope import component
from zope import interface

from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.i18n.locales.browser.selector import LanguageSelector

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.lingualinks import msgids
from collective.portlet.lingualinks import interfaces
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

class ILinguaLinksSchema(IPortletDataProvider):
    """schema of the portlet"""
    
    
class Assignment(base.Assignment):
    interface.implements(ILinguaLinksSchema)

    @property
    def title(self):
        return msgids.portlet_title


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self._site_settings = None
        self._portal_url = None

    def render(self):
        return self._template()

    @property
    def available(self):
        """Show the portlet only if there are one or more elements."""
        return True

    def translations(self):
        all_translations = self.context.getTranslations()
        clang = self.context.Language()
        translations = {}

        for language in all_translations:
            if language != clang:
                translations[language] = all_translations[language]

        return translations
    
    def languages(self):
        tool = getToolByName(self.context, 'portal_languages')
        return tool.getAvailableLanguageInformation()

    def get_links(self):
        translations = self.translations()
        settings = self.site_settings()
        if settings.compute_url == 'navigation_root':
            return self.get_links_navigation_root(translations)
        else:
            return self.get_links_domain_name(translations)

    def get_links_navigation_root(self, translations):
        links = []
        languages = self.languages()

        for language in translations:
            obj = translations[language][0]
            links.append({'url': obj.absolute_url(),
                          'name': languages.get(language).get('native')})

        return links

    def get_links_domain_name(self, translations):
        links = []
        languages = self.languages()
        mapping = self.url_mapping()
        navroot_path = self.navigation_root_path()

        for language in translations:
            site_url = mapping.get(language,None)

            if not site_url:
                continue

            obj = translations[language][0]
            path = obj.getPhysicalPath()
            url = site_url + '/'.join(path[len(navroot_path):])

            links.append({'url': url,
                          'name': languages.get(language).get('native')})

        return links

    def site_settings(self):
        if self._site_settings is None:
            registry = component.getUtility(IRegistry)
            self._site_settings = registry.forInterface(interfaces.ILinguaLinksConfigurationSchema)
        return self._site_settings

    def portal_url(self):
        if self._portal_url is None:
            portal_state = component.getMultiAdapter((self.context,
                                                      self.request),
                                                     name=u'plone_portal_state')
            self._portal_url = portal_state.portal_url()

        return self._portal_url

    def navigation_root_path(self):
        context = aq_inner(self.context)
        pstate = component.getMultiAdapter((context, self.request),
                                           name=u'plone_portal_state')
        return pstate.navigation_root_path().split('/')

    def url_mapping(self):
        url_mapping = {}
        mappings = self.site_settings().url_mapping

        if mappings is None:
            mappings = []

        for mapping in mappings:
            code,url = mapping.split('|')
            url_mapping[code]=url

        return url_mapping


class AddForm(base.NullAddForm):
    """Empty forms, configuration is taken from site control panel"""

    def create(self):
        return Assignment()

