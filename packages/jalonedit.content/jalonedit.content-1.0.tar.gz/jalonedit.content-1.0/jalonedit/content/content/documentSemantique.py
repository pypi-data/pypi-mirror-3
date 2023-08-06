# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalonedit.content import contentMessageFactory as _
from jalonedit.content.config import PROJECTNAME
from jalonedit.content.interfaces import IDocumentSemantique

from DateTime import DateTime

contenuDocumentSemantique = [u"Pas d'encadré".encode("utf-8"),
                             u"Objectifs".encode("utf-8"),
				             u"Commentaire".encode("utf-8"),
					         u"Extrait".encode("utf-8"),
					         u"Pré-requis".encode("utf-8"),
					         u"Présentation".encode("utf-8"),
					         u"Introduction".encode("utf-8"),
					         u"Conclusion".encode("utf-8"),
					         u"Exemple".encode("utf-8"),
					         u"Complément".encode("utf-8"),
					         u"En savoir plus".encode("utf-8"),
					         u"Explication".encode("utf-8"),
					         u"Définition".encode("utf-8"),
					         u"Remarque".encode("utf-8"),
					         u"Méthode".encode("utf-8"),
					         u"Rappel".encode("utf-8"),
					         u"Attention".encode("utf-8"),
					         u"Syntaxe".encode("utf-8"),
					         u"Conseil".encode("utf-8"),
					         u"Confère".encode("utf-8"),
					         u"Citation".encode("utf-8"),
					         u"Activité".encode("utf-8")]

DocumentSemantiqueSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField(
        "typeSemantique",
        required = False,
        accessor = "getTypeSemantique",
        default = 0,
        searchable = False,
        vocabulary = contenuDocumentSemantique,
        widget = atpublic.SelectionWidget(
            label = _(u"label_typeSemantique", default=u"Type"),
            description = _(u"desc_typeSemantique", default=u"Description du type"),
            format = "select"
            )),
    ))

class DocumentSemantique(ATDocumentBase):
    """ Un document sémantique pour JalonEdit
    """

    implements(IDocumentSemantique)
    meta_type = 'DocumentSemantique'
    schema = DocumentSemantiqueSchema
    schema['title'].required = False
    schema['title'].mode = "r"
    schema['description'].required = False
    schema['description'].mode = "r"

    def getClassSemantique(self, contenuSemantique):
        """ Correspondance entre le type de contenu et la classe
        """
        dicoContenuSemantique = {u"Pas d'encadré".encode("utf-8")  : "rien",
                                 u"Introduction".encode("utf-8")   : "introduction",
                                 u"Conclusion".encode("utf-8")     : "conclusion",
                                 u"Exemple".encode("utf-8")        : "exemple",
                                 u"Extrait".encode("utf-8")        : "extrait", 
                                 u"Complément".encode("utf-8")     : "complement",
                                 u"Commentaire".encode("utf-8")    : "commentaire",
                                 u"En savoir plus".encode("utf-8") : "ensavoirplus", 
                                 u"Explication".encode("utf-8")    : "explication", 
                                 u"Définition".encode("utf-8")     : "definition", 
                                 u"Remarque".encode("utf-8")       : "remarque", 
                                 u"Méthode".encode("utf-8")        : "methode", 
                                 u"Rappel".encode("utf-8")         : "rappel", 
                                 u"Attention".encode("utf-8")      : "attention", 
                                 u"Syntaxe".encode("utf-8")        : "syntaxe", 
                                 u"Conseil".encode("utf-8")        : "conseil", 
                                 u"Confère".encode("utf-8")        : "confere", 
                                 u"Citation".encode("utf-8")       : "citation",
                                 u"Pré-requis".encode("utf-8")     : "prerequis",
                                 u"Objectifs".encode("utf-8")      : "objectifs",
                                 u"Présentation".encode("utf-8")   : "presentation",
                                 u"Activité".encode("utf-8")       : "activite"}
        if contenuSemantique == u"Pas d'encadré".encode("utf-8"): return "document"
        else: return "bloc-expositif bloc-%s" % dicoContenuSemantique[contenuSemantique]

registerATCT(DocumentSemantique, PROJECTNAME)
