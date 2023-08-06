# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalonedit.content import contentMessageFactory as _
from jalonedit.content.config import PROJECTNAME
from jalonedit.content.interfaces import IVideo

from DateTime import DateTime


VideoSchema = ATDocumentSchema.copy()

class Video(ATDocumentBase):
    """ Un document de bloc présentation pour 
    """

    implements(IVideo)
    meta_type = 'Video'
    schema = VideoSchema
    schema['description'].title = "Lecteur exportable"
    schema['description'].required = True
    schema['text'].mode = "r"

    def getAffichage(self):
        return "toto titi tata"

registerATCT(Video, PROJECTNAME)
