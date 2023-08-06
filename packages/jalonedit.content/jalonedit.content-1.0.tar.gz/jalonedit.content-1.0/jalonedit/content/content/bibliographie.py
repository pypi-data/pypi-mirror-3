# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalonedit.content import contentMessageFactory as _
from jalonedit.content.config import PROJECTNAME
from jalonedit.content.interfaces import IBibliographie

from DateTime import DateTime

BibliographieSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField(
        "sous-titre",
        required = False,
        accessor = "getSousTitre",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_sousTitreWebographie", default=u"sous Titre Webographie"),
            description = _(u"desc_sousTitreWebographie", default=u"Description du sous Titre Webographie"),
            )),
    atpublic.StringField(
        "premier-auteur",
        required = True,
        accessor = "getPremierAuteur",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_premierAuteur", default=u"premier Auteur"),
            description = _(u"desc_premierAuteur", default=u"Description du premier Auteur"),
            )),
    atpublic.TextField(
        "autres-auteurs",
        required = False,
        accessor = "getAutresAuteurs",
        searchable = False,
        widget = atpublic.TextAreaWidget(
            label = _(u"label_autresAuteurs", default=u"autres Auteurs"),
            description = _(u"desc_autresAuteurs", default=u"Description des autres Auteurs"),
            )),
    atpublic.StringField(
        "volume",
        required = False,
        accessor = "getVolume",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_volume", default=u"Volume"),
            description = _(u"desc_volume", default=u"Description du volume"),
            )),
    atpublic.StringField(
        "lieu",
        required = False,
        accessor = "getLieu",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_lieu", default=u"Lieu"),
            description = _(u"desc_lieu", default=u"Description du lieu"),
            )),
    atpublic.StringField(
        "editeur",
        required = True,
        accessor = "getEditeur",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_editeur", default=u"Editeur"),
            description = _(u"desc_editeur", default=u"Description de l'editeur"),
            )),
    atpublic.IntegerField(
        "annee",
        required = True,
        accessor = "getAnnee",
        searchable = False,
        widget = atpublic.IntegerWidget(
            label = _(u"label_annee", default=u"Annee"),
            description = _(u"desc_annee", default=u"Description de l'annee"),
            )),
    atpublic.StringField(
        "pagination",
        required = False,
        accessor = "getPagination",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_pagination", default=u"Pagination"),
            description = _(u"desc_pagination", default=u"Description de la pagination"),
            )),
    atpublic.StringField(
        "collection",
        required = False,
        accessor = "getCollection",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_collection", default=u"Collection"),
            description = _(u"desc_collection", default=u"Description de la collection"),
            )),
    atpublic.StringField(
        "isbn",
        required = False,
        accessor = "getISBN",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_isbn", default=u"ISBN"),
            description = _(u"desc_isbn", default=u"Description de l'isbn"),
            )),
    atpublic.StringField(
        "urlbiblio",
        required = False,
        accessor = "getURLWEB",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"label_urlbiblio", default=u"URL bibliographie"),
            description = _(u"desc_urlbiblio", default=u"Description de l'URL bibliographie"),
            )),
    atpublic.TextField(
        "autre",
        required = False,
        accessor = "getAutre",
        searchable = False,
        widget = atpublic.TextAreaWidget(
            label = _(u"label_autre", default=u"Autre"),
            description = _(u"desc_autre", default=u"Description de autre"),
            )),
    ))

class Bibliographie(ATDocumentBase):
    """ Un document de bloc présentation pour 
    """

    implements(IBibliographie)
    meta_type = 'Bibliographie'
    schema = BibliographieSchema
    schema['description'].required = False
    schema['description'].mode = "r"

    """
    def post_validate(self, REQUEST=None, errors=None):
        now_day = DateTime().day()
        if int(REQUEST.form['note']) > int(now_day):
            errors["note"] = _(u"erreur_note", default=u"La note doit être inférieur à la date du jour")
   """

registerATCT(Bibliographie, PROJECTNAME)
