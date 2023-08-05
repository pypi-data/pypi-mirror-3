# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from App.class_init import InitializeClass as initializeClass
from Products.Five.security import protectName

from five import grok
from grokcore.view.meta.views import TemplateGrokker
from zope.interface import Interface
from zope.component import adaptedBy, provideAdapter
import martian

from infrae.rest.components import REST, ALLOWED_REST_METHODS
from infrae.rest.components import RESTWithTemplate
from infrae.rest.interfaces import IRESTComponent

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

def default_context(*stuff, **things):
    return None


class RESTGrokker(martian.ClassGrokker):
    """Grok REST views.
    """
    martian.component(REST)
    martian.directive(grok.context, get_default=default_context)
    martian.directive(grok.name, get_default=default_view_name)
    martian.directive(grok.require, name='permission')

    def execute(self, factory, context, name, permission, config, **kw):
        """Register the REST component as a view on the IREST layer.
        """
        if permission is None:
            permission = 'zope.Public'

        adapts = adaptedBy(factory)
        if adapts is None:
            adapts = (Interface, context)

        config.action(
            discriminator=('adapter', adapts, IRESTComponent, name),
            callable=provideAdapter,
            args=(factory, adapts, IRESTComponent, name))

        for method in ALLOWED_REST_METHODS:
            if hasattr(factory, method):
                config.action(
                    discriminator = ('five:protectName', factory, method),
                    callable = protectName,
                    args = (factory, method, permission))

        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,))
        return True


class RESTWithTemplateGrokker(TemplateGrokker):
    martian.component(RESTWithTemplate)

    def has_render(self, factory):
        return False

    def has_no_render(self, factory):
        return False

