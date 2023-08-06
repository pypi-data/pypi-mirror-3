# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalonedit.content.content.blocPresentation import contenuPresentation

class Presentation(BrowserView):
    """Class pour le presentation.pt
    """
        
    def getTypesContenus(self):
        return contenuPresentation
    
    def getContenusPresentation(self):
        retour = {}
        for key in contenuPresentation: retour[key] = []
        for document in self.context.objectValues("BlocPresentation"):
            retour[document.getTypePresentation()].append(document.getText())
        
        return retour