from zope import interface
from zope import schema

from plone.app.registry.browser import controlpanel

from collective.portlet.lingualinks import msgids

class ILinguaLinksConfigurationSchema(interface.Interface):
    """Define configuration schema"""

    compute_url = schema.Choice(title=msgids.use_portal_url_label,
                                description=msgids.use_portal_url_desc,
                                values=['navigation_root','domain_name'])

    url_mapping = schema.List(title=msgids.url_mapping_label,
                              description=msgids.url_mapping_desc,
                              required=False,
                              value_type=schema.ASCIILine(title=msgids.lang_url_label))

class ControlPanelForm(controlpanel.RegistryEditForm):
    schema = ILinguaLinksConfigurationSchema

class ControlPanelPage(controlpanel.ControlPanelFormWrapper):
    """Page to display the form"""
    form = ControlPanelForm
    label = msgids.controlpanel_label
