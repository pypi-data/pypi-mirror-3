# -*- coding: utf-8 -*-

import string 
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

class Ressource(BrowserView):
    """Class pour le presentation.pt
    """
        
    def getTypesContenus(self):
        return [u"glossaire".encode("utf-8"), u"bibliographie".encode("utf-8"), u"webographie".encode("utf-8")]
    
    def getContenusRessource(self, typeContenu):
        dicoLettres = {"#" : []}
        for lettre in string.ascii_uppercase:
            dicoLettres[lettre] = []
        if typeContenu == u"glossaire".encode("utf-8"): 
           contenus = self.context.objectValues("Glossaire")
           for contenu in contenus:
               if contenu.Title().capitalize()[0] in string.ascii_uppercase:
                  dicoLettres[contenu.Title().capitalize()[0]].append({"title" : contenu.Title().capitalize(), "definition" : contenu.getText()})
               else:
                  dicoLettres["#"].append({"title" : contenu.Title().capitalize(), "definition" : contenu.getText()})
        if typeContenu == u"webographie".encode("utf-8"): 
           contenus = self.context.objectValues("ATLink")
           for contenu in contenus:
               if contenu.Title().capitalize()[0] in string.ascii_uppercase:
                  dicoLettres[contenu.Title().capitalize()[0]].append({"title" : contenu.Title().capitalize(), "description" : contenu.Description(), "lien" : contenu.getRemoteUrl()})
               else:
                  dicoLettres["#"].append({"title" : contenu.Title().capitalize(), "description" : contenu.Description(), "lien" : contenu.getRemoteUrl()})
        if typeContenu == u"bibliographie".encode("utf-8"): 
           contenus = self.context.objectValues("Bibliographie")
           for contenu in contenus:
               if contenu.Title().capitalize()[0] in string.ascii_uppercase:
                  dicoLettres[contenu.Title().capitalize()[0]].append({"title" : contenu.Title().capitalize()
                                                                     ,"description" : contenu.getText()
                                                                     ,"sous-titre" : contenu.getSousTitre()
                                                                     ,"premier-auteur" : contenu.getPremierAuteur()
                                                                     ,"autres-auteurs" : contenu.getAutresAuteurs()
                                                                     ,"volume" : contenu.getVolume()
                                                                     ,"lieu" : contenu.getLieu()
                                                                     ,"editeur" : contenu.getEditeur()
                                                                     ,"annee" : contenu.getAnnee()
                                                                     ,"pagination" : contenu.getPagination()
                                                                     ,"collection" : contenu.getCollection()
                                                                     ,"isbn" : contenu.getISBN()
                                                                     ,"urlbiblio" : contenu.getURLWEB()
                                                                     ,"autre" : contenu.getAutre()})
               else:
                  dicoLettres["#"].append({"title" : contenu.Title().capitalize()
                                                                     ,"description" : contenu.getText()
                                                                     ,"sous-titre" : contenu.getSousTitre()
                                                                     ,"premier-auteur" : contenu.getPremierAuteur()
                                                                     ,"autres-auteurs" : contenu.getAutresAuteurs()
                                                                     ,"volume" : contenu.getVolume()
                                                                     ,"lieu" : contenu.getLieu()
                                                                     ,"editeur" : contenu.getEditeur()
                                                                     ,"annee" : contenu.getAnnee()
                                                                     ,"pagination" : contenu.getPagination()
                                                                     ,"collection" : contenu.getCollection()
                                                                     ,"isbn" : contenu.getISBN()
                                                                     ,"urlbiblio" : contenu.getURLWEB()
                                                                     ,"autre" : contenu.getAutre()})   
        return dicoLettres
        
    def selectedClass(self, left, right):
        if left==right:
            return "selected"
        else:
            return "plain"
        
        