Introduction
============
This package allows you to define a set of views, schemas, and templates that 
can be used as templates for a view on a Plone site.

So basically, it just allows an easy mechanism to provide extra, reusable 
templates that have settings attached to them. Each template that you fill
in the settings for, can then be referenced from another template view
on the site elsewhere.


Basic example
-------------

Define your settings::

>>> class ICustomSettings(Interface):
>>>     setting_one = schema.TextLine(title=u'Setting One')
>>>     setting_two = schema.Text(title=u'Setting Two', default=u'')

Define a template view utility::

>>> from wildcard.templatedviews.browser import BaseViewUtility
>>> from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
>>> class CustomTemplateViewUtility(BaseViewUtility):
>>>     settings = ICustomSettings
>>>     _for = None
>>>     title = u'Custom Template'
>>>     description = u'a custom template settings.'
>>>     custom_widgets = (
>>>         ('setting_one', WYSIWYGWidget),
>>>     )


And wire it up with zcml::

>>> <browser:page
>>>   for="*"
>>>   name="custom-template"
>>>   class="wildcard.templatedviews.browser.BaseView"
>>>   template="templates/custom-template.pt"
>>>   permission="zope2.View"
>>> />
>>> <utility factory=".CustomTemplateViewUtility" name="custom-template" />
>>> <adapter 
>>>   for="*"
>>>   provides=".ICustomSettings"
>>>   factory="wildcard.templatedviews.settings.TemplateViewSettings"
>>> />

Then in your `custom-template.pt`, you can use the settings like this::

>>> <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
>>>       xmlns:tal="http://xml.zope.org/namespaces/tal"
>>>       xmlns:metal="http://xml.zope.org/namespaces/metal"
>>>       xmlns:i18n="http://xml.zope.org/namespaces/i18n"
>>>       lang="en"
>>>       metal:use-macro="here/main_template/macros/master"
>>>       i18n:domain="plone">
>>> <body>
>>>
>>> <metal:main fill-slot="main" tal:define="settings python: view.settings">
>>>   <tal:main-macro metal:define-macro="main">
>>>     <h1 tal:content="python: settings.setting_one" />
>>>     <p tal:content="structure python: settings.setting_two" />
>>>   </tal:main-macro>
>>> </metal:main>
>>> </body>
>>> </html>

You'll also need to add the 'templated-view' view to the list of available
views on the content type you'd like to use this for.

Now to use it after you've installed it, select "templated-view" from the
display drop down, then use the "Select Template" and "Template Settings"
to customize your templated view.

Check out the source for more examples on how to use it.

