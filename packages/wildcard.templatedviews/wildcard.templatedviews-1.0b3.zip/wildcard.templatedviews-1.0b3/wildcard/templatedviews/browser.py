from Products.Five import BrowserView
from wildcard.templatedviews.settings import TemplatedSettings, TemplateViewSettings
from wildcard.templatedviews.interfaces import ITemplated, IBaseSettings, \
    ITemplatedSettings, ITemplatedView, IReferencedTemplate
from zope.component import getMultiAdapter, queryUtility
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from plone.memoize.view import memoize
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from zope.app.component.hooks import getSite
from wildcard.templatedviews.events import TemplateSettingsFormEvent, TemplateSelectedFormEvent
import zope.event

class BaseViewUtility(object):
    implements(ITemplated)
    settings = IBaseSettings
    _for = None
    title = u'Empty Default'
    description = u'You need to select a template'
    custom_widgets = ()
    field_order = None
    
class ReferencedViewUtility(BaseViewUtility):
    settings = IReferencedTemplate
    title = u'Referenced Template'
    description = u'Select a page you would like to use the template and settings of.'
    
    custom_widgets=(
        ('reference', UberSelectionWidget),
    )
    
def get_settings(context, site=None):
    if not site:
        site = getSite()
    template_name = TemplatedSettings(context).template_name or 'base-template-view'
    if template_name == 'referenced-template-view':
        tmplsettings = TemplateViewSettings(context)
        ref = tmplsettings.val('reference')
        if ref:
            return get_settings(ref, site)
            
    return TemplateViewSettings(context)

class BaseView(BrowserView):
    
    @property
    @memoize
    def settings(self):
        return get_settings(self.context)

    def get_settings(self, context):
        return get_settings(context)

    def get_view(self, name):
        view = getMultiAdapter((self.context, self.request), name=name)
        return view.__of__(self.context)

def get_template_name(context, site=None):
    if not site:
        site = getSite()
    settings = TemplatedSettings(context)
    template_name = settings.template_name or 'base-template-view'
    
    if template_name == 'referenced-template-view':
        tmplsettings = TemplateViewSettings(context)
        ref = tmplsettings.val('reference')
        if ref:
            return get_template_name(ref, site)
    return template_name

class TemplateView(BrowserView):
    """
    All this view does is find the correct template
    and render it here in place instead of this view.
    """
    implements(ITemplatedView)
    
    @memoize
    def enabled(self):
        utils = getToolByName(self.context, 'plone_utils')
        try:
            return self.context.getLayout() == 'templated-view' or \
                utils.browserDefault(self.context)[1][0] == "templated-view"
        except:
            return False
    
    def __call__(self, *args, **kwargs):
        template_name = get_template_name(self.context)
        util = queryUtility(ITemplated, name=template_name)
        if not util:
            template_name = 'base-template-view'
        
        view = getMultiAdapter((self.context, self.request), name=template_name)
        return view.__of__(self.context)(*args, **kwargs)
        
        
from plone.app.form import base as ploneformbase
from zope.formlib import form

class SelectTemplateForm(ploneformbase.EditForm):
    form_fields = form.FormFields(ITemplatedSettings)
    
    label = u'Select template'
    description = u'select a templated view to use'

    @form.action(u"Save", condition=form.haveInputWidgets, name=u'save')
    def _handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            self.status = "Changes saved"
            zope.event.notify(TemplateSelectedFormEvent(self.context))
        else:
            self.status = "No changes"
        self.request.response.redirect(self.context.absolute_url() + '/view')
    
class TemplateSettingsForm(ploneformbase.EditForm):    
    label = u'Template settings'
    description = u''
    
    def __init__(self, *args, **kwargs):
        super(TemplateSettingsForm, self).__init__(*args, **kwargs)
        settings = TemplatedSettings(self.context)
        util = queryUtility(ITemplated, name=settings.template_name)
        if not util:
            util = BaseViewUtility()
            
        self.description = util.description
        self.form_fields = form.FormFields(util.settings)
        if util.field_order:
            self.form_fields = self.form_fields.select(*util.field_order)
        for name, widget in util.custom_widgets:
            try:
                self.form_fields[name].custom_widget = widget
            except KeyError:
                # can't find field
                pass
                

    @form.action(u"Save", condition=form.haveInputWidgets, name=u'save')
    def _handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            self.status = "Changes saved"
            zope.event.notify(TemplateSettingsFormEvent(self.context))
        else:
            self.status = "No changes"
        self.request.response.redirect(self.context.absolute_url() + '/view')
