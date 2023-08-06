# -*- coding: utf-8 -*-
from zope.interface import implements
from Acquisition import aq_inner
from plone.app.layout.globals.interfaces import IContextState
from plone.app.layout.globals.context import ContextState as BaseClass


class ContextState(BaseClass):
    """
    edit Folder method that allows to add elements to Structured Document also when he's set ad default view
    """
    implements(IContextState)

    def folder(self):
        if self.is_structural_folder():
            return aq_inner(self.context)
        else:
            return self.parent()
