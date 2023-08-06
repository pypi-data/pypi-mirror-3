"""
A grok.EditForm is a special grok.View that renders an edit form.

  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/manfred/@@edit")
  >>> browser.getControl(name="form.name").value = "Manfred the Mammoth"
  >>> browser.getControl(name="form.size").value = "Really big"
  >>> browser.getControl("Apply").click()
  >>> print browser.contents
  <html>...
  ...Manfred the Mammoth...
  ...Really big...
  ...

grok.DisplayForm renders a display form:

  >>> browser.open("http://localhost/manfred/@@display")
  >>> print browser.contents
  <html>...
  ...Manfred the Mammoth...
  ...Really big...
  ...

"""
import grokcore.formlib as grok
from zope import schema
from zope.interface import Interface, implements
from zope.schema.fieldproperty import FieldProperty

class IMammoth(Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size", default=u"Quite normal")

class Mammoth(grok.testing.Model):
    implements(IMammoth)
    grok.testing.protect_get(grok.Public, 'name', 'size')
    grok.testing.protect_set(grok.Public, 'name', 'size')
    
    name = FieldProperty(IMammoth['name'])    
    size = FieldProperty(IMammoth['size'])    

class Edit(grok.EditForm):
    pass

class Display(grok.DisplayForm):
    pass
