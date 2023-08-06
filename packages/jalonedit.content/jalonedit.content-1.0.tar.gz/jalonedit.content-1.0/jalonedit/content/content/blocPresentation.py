# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalonedit.content import contentMessageFactory as _
from jalonedit.content.config import PROJECTNAME
from jalonedit.content.interfaces import IBlocPresentation

from DateTime import DateTime

contenuPresentation = [u"Description".encode("utf-8"), u"Pré-requis".encode("utf-8"), u"Objectifs".encode("utf-8")]

BlocPresentationSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField(
        "typePresentation",
        required = False,
        accessor = "getTypePresentation",
        default = 0,
        searchable = False,
        vocabulary = contenuPresentation,
        widget = atpublic.SelectionWidget(
            label = _(u"label_typePresentation", default=u"Type"),
            description = _(u"desc_typePresentation", default=u"Description du type"),
            format = "select"
            )),
    ))

class BlocPresentation(ATDocumentBase):
    """ Un document de bloc présentation pour JalonEdit
    """

    implements(IBlocPresentation)
    meta_type = 'BlocPresentation'
    schema = BlocPresentationSchema
    schema['title'].required = False
    schema['title'].mode = "r"
    schema['description'].required = False
    schema['description'].mode = "r"

registerATCT(BlocPresentation, PROJECTNAME)
