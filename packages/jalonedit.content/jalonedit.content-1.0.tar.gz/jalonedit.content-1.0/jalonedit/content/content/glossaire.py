# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalonedit.content import contentMessageFactory as _
from jalonedit.content.config import PROJECTNAME
from jalonedit.content.interfaces import IGlossaire

from DateTime import DateTime

GlossaireSchema = ATDocumentSchema.copy()

class Glossaire(ATDocumentBase):
    """ Un mot de glossaire
    """

    implements(IGlossaire)
    meta_type = 'Glossaire'
    schema = GlossaireSchema
    schema['description'].required = False
    schema['description'].mode = "r"

registerATCT(Glossaire, PROJECTNAME)
