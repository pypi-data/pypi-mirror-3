from Products.CMFCore.utils import getToolByName
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.interface import implements
from persistent.dict import PersistentDict
from zope import schema
from zope.annotation.interfaces import IAnnotations
from wildcard.templatedviews.interfaces import ITemplatedSettings, \
    ITemplated
from zope.component import getUtility
from zope.app.component.hooks import getSite
from zope.schema.interfaces import IContextSourceBinder

VIEW_ANNOTATION_KEY = 'wildcard.templatedviews.viewsettings'
TEMPLATE_ANNOTATION_KEY = 'wildcard.templatedviews.templatesettings'


class TemplatedSettings(object):
    """
    """
    implements(ITemplatedSettings)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)

        self._metadata = annotations.get(VIEW_ANNOTATION_KEY, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[VIEW_ANNOTATION_KEY] = self._metadata

    def __setattr__(self, name, value):
        if name in ('context', '_metadata'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def __getattr__(self, name):
        """
        """
        if name in ITemplatedSettings.names():
            default = ITemplatedSettings[name].default
        else:
            default = None

        return self._metadata.get(name, default)


class addressablelist(list):
    def __getattr__(self, name):
        if name.isdigit():
            index = int(name)
            if len(self) > index:
                return self[index]
            else:
                return None
        return super(addressablelist, self).__getattr__(name)


class TemplateViewSettings(object):

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        settings = TemplatedSettings(context)
        self.site = getSite()
        self.site_path = '/'.join(self.site.getPhysicalPath())
        util = getUtility(ITemplated, name=settings.template_name)
        self._interface = util.settings
        self.redirect_storage = getUtility(IRedirectionStorage)
        self.transformer = getToolByName(context, 'portal_transforms', None)

        self._metadata = annotations.get(TEMPLATE_ANNOTATION_KEY, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[TEMPLATE_ANNOTATION_KEY] = self._metadata

    def __setattr__(self, name, value):
        if name in ('context', '_metadata', '_interface',
                    'site', 'site_path', 'redirect_storage', 'transformer'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def lookupRedirect(self, item):
        newpath = self.redirect_storage.get(self.site_path + item, None)
        if newpath:
            return self.get_content(newpath)

    def get_content(self, item):
        obj = self.context.restrictedTraverse(self.site_path + item, None)
        if not obj:
            # look this guy up as alias
            return self.lookupRedirect(item)
        else:
            return obj

    def isContent(self, field):
        return (type(field) == schema.Choice and hasattr(field, 'source') \
            and IContextSourceBinder.providedBy(field.source)) or \
            (type(field) == schema.List and \
            hasattr(field.value_type, 'source') and \
            IContextSourceBinder.providedBy(field.value_type.source))

    def val(self, name):
        is_content = False
        field = self._interface.get(name)
        if field:
            if self.isContent(field):
                is_content = True

        result = getattr(self, name)
        if type(result) in (list, set, tuple):
            result = addressablelist(result)
        if is_content and result:
            if type(result) == addressablelist:
                old = result
                result = addressablelist()
                for item in old:
                    result.append(self.get_content(item))
            else:
                result = self.get_content(result)
        if isinstance(result, basestring):
            if result:
                orig = result
                if not isinstance(orig, unicode):
                    # Don't really know if this code is needed here
                    orig = unicode(orig, 'utf-8', 'ignore')

                # Portal transforms needs encoded strings
                orig = orig.encode('utf-8')
                result = self.transformer.convertTo('text/x-html-safe', orig,
                    context=self.context, mimetype='text/html')
                data = result.getData()

                if data:
                    return unicode(data, 'utf-8', errors='ignore')
        return result

    def __getattr__(self, name):
        """
        """
        field = self._interface.get(name)
        if field:
            default = field.default
        else:
            default = None

        return self._metadata.get(name, default)
