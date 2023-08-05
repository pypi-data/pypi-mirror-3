from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from wildcard.templatedviews.interfaces import ITemplateSelectedFormSaved, ITemplateSettingsFormSaved

class TemplateSelectedFormEvent(ObjectEvent):
    
   def __init__(self, object):
      self.object = object

   implements(ITemplateSelectedFormSaved)

class TemplateSettingsFormEvent(ObjectEvent):
    
   def __init__(self, object):
      self.object = object

   implements(ITemplateSettingsFormSaved)
