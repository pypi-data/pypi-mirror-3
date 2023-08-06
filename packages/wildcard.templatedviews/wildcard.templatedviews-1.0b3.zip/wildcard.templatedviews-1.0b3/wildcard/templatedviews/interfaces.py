from zope.interface import Interface, Attribute
from zope import schema
from wildcard.templatedviews.vocabularies import SettingsContextSourceBinder

class IBaseSettings(Interface):
    pass

class ITemplated(Interface):
    settings = Attribute("An inteface that defines the settings for this template.")
    _for = Attribute("An interface that describes what this utility is enable for or None if available for all.")
    title = Attribute("")
    description = Attribute("")
    custom_widget = Attribute("A tuple of (field name, widget) to use on the form")
    field_order = Attribute("A custom order the fields should be in on the form.")
    
class ITemplatedSettings(Interface):
    
    template_name = schema.Choice(
        title=u'Template',
        required=True,
        default=u'base-template-view',
        vocabulary="wildcard.templatedviews.templates"
    )
    
class ILayer(Interface):
    pass
    
class ITemplatedView(Interface):
    def enabled():
        pass
        
        
class IReferencedTemplate(Interface):
    reference = schema.Choice(
        title=u'Referenced item',
        description=u'Select an item you would like to use the template of',
        required=True,
        source=SettingsContextSourceBinder({}, default_query='path:')
    )

class ITemplateSelectedFormSaved(Interface):
    pass

class ITemplateSettingsFormSaved(Interface):
    pass

