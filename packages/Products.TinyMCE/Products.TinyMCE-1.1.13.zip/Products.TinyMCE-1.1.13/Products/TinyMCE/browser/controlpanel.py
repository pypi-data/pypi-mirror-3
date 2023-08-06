from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from Products.TinyMCE.interfaces.utility import ITinyMCELayout
from Products.TinyMCE.interfaces.utility import ITinyMCEToolbar
from Products.TinyMCE.interfaces.utility import ITinyMCELibraries
from Products.TinyMCE.interfaces.utility import ITinyMCEResourceTypes

from Products.TinyMCE.browser.interfaces.controlpanel import ITinyMCEControlPanelForm
from Products.TinyMCE.setuphandlers import install_mimetype_and_transforms, uninstall_mimetype_and_transforms

_ = MessageFactory('plone.tinymce')


class TinyMCEControlPanelForm(ControlPanelForm):
    """TinyMCE Control Panel Form"""
    implements(ITinyMCEControlPanelForm)

    tinymcelayout = FormFieldsets(ITinyMCELayout)
    tinymcelayout.id = 'tinymcelayout'
    tinymcelayout.label = _(u'Layout')

    tinymcetoolbar = FormFieldsets(ITinyMCEToolbar)
    tinymcetoolbar.id = 'tinymcetoolbar'
    tinymcetoolbar.label = _(u'Toolbar')

    tinymcelibraries = FormFieldsets(ITinyMCELibraries)
    tinymcelibraries.id = 'tinymcelibraries'
    tinymcelibraries.label = _(u'Libraries')

    tinymceresourcetypes = FormFieldsets(ITinyMCEResourceTypes)
    tinymceresourcetypes.id = 'tinymceresourcetypes'
    tinymceresourcetypes.label = _(u'Resource Types')

    form_fields = FormFieldsets(tinymcelayout, tinymcetoolbar, tinymceresourcetypes) # tinymcelibraries

    label = _(u"TinyMCE Settings")
    description = _(u"Settings for the TinyMCE Wysiwyg editor.")
    form_name = _("TinyMCE Settings")

    def _on_save(self, data=None):
        """On save event handler"""
        if self.context.link_using_uids or self.context.allow_captioned_images:
            # We need to register our mimetype and transforms for uid links and captioned_images
            install_mimetype_and_transforms(self.context)
        else:
            # Unregister them
            uninstall_mimetype_and_transforms(self.context)
