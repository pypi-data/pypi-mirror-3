===========
infrae.rest
===========

``infrae.rest`` provide a simple way to write REST APIs in Zope 2.

API
===

REST component
--------------

``infrae.rest`` provides mainly a base class ``REST`` which behave a
lot like a Grok view::

   from infrae.rest import REST

   class MyAction(REST):
       """My action REST API.
       """

       def POST(self, name, value):
           # Called by POST /content/++rest++myaction&name=foo?value=bar
           return 'Success'

       def GET(self):
           # Called by GET /content/++rest++myaction
           values = self.context.something()
           return self.json_response(values)


You just have to grok your package to make it available.

- You can provide: ``POST``, ``GET``, ``HEAD``, ``DELETE`` requests.

- You can use the directives ``grok.name``, ``grok.require`` and
  ``grok.context`` to configure your REST API. They work exactly like
  on a ``grok.View``.


Nesting REST component
----------------------

You can nest REST component. In that you should use the grok directive
adapts in order to define which is the parent handler, and the
context::

   from infrae.rest import REST
   from five import grok
   from OFS.Folder import Folder

   class ParentHandler(REST):
       grok.context(Folder)

       def GET(self):
           # Called by GET /folder/++rest++parenthandler
           return u'Hello'


   class ChildHandler(REST):
       grok.adapts(ParentHandler, Folder)

       def GET(self):
           # Called by GET /folder/++rest++parenthandler/childhandler
           return u'Child


RESTWithTemplate component
--------------------------

You can alternatively use the base class ``RESTWithTemplate``. The
only difference is that your class will be associated to a Grok
template automatically.


