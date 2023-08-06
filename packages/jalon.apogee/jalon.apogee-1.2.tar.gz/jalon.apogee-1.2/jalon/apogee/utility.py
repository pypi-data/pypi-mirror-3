# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.apogee.interfaces.utility import IApogee, IApogeeLayout

from OFS.SimpleItem import SimpleItem

# Imports
import json
from DateTime import DateTime

import tables

# SQL Alchemy
from sqlalchemy import create_engine, and_, or_, distinct
from sqlalchemy.sql import func, text
from sqlalchemy.orm import sessionmaker, aliased


def form_adapter(context):
    """Form Adapter"""
    return getUtility(IApogee)


class Apogee(SimpleItem):
    """Apogee Utility"""
    implements(IApogee)
    classProvides(
        IApogeeLayout,
        )
    security = ClassSecurityInfo()

    # Parametres généraux
    url_connexion = FieldProperty(IApogeeLayout['url_connexion'])
    cod_anu = FieldProperty(IApogeeLayout['cod_anu'])
    uel = FieldProperty(IApogeeLayout['uel'])
    sessionApogee = None
    Session = sessionmaker()

    #debug = []

    # Parametres spécifiques
    def getAttribut(self, attribut):
        return self.__getattribute__(attribut)

    def getGroupesEtudiant(self, COD_ETU):
        GPE = aliased(tables.Groupe)
        GPO = aliased(tables.GpeObj)
        IAG = aliased(tables.IndAffecteGpe)
        IND = aliased(tables.Individu)
        session = self.getSession()
        recherche = session.query(IAG.COD_GPE, GPE.LIB_GPE, GPE.COD_EXT_GPE, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).outerjoin(GPE, IAG.COD_GPE==GPE.COD_GPE).outerjoin(GPO, GPE.COD_GPE==GPO.COD_GPE).outerjoin(IND, IAG.COD_IND==IND.COD_IND).filter(and_(IAG.COD_ANU==int(self.cod_anu), GPE.LIB_GPE <> None, IND.COD_ETU==COD_ETU)).group_by(IAG.COD_GPE, GPE.LIB_GPE, GPE.COD_EXT_GPE, GPE.COD_EXT_GPE, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).order_by(GPE.LIB_GPE)
        #session.close()
        return recherche.all()

    def getTousEtudiantsGroupes(self):
        GPE = aliased(tables.Groupe)
        GPO = aliased(tables.GpeObj)
        IAG = aliased(tables.IndAffecteGpe)
        IND = aliased(tables.Individu)
        session = self.getSession()
        recherche = session.query(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND).outerjoin(GPE, IAG.COD_GPE==GPE.COD_GPE).outerjoin(GPO, GPE.COD_GPE==GPO.COD_GPE).outerjoin(IND, IAG.COD_IND==IND.COD_IND).filter(and_(IAG.COD_ANU==int(self.cod_anu), GPE.LIB_GPE <> None)).group_by(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND)
        #session.close()
        return recherche.all()

    def getInfosEtape(self, COD_ETP, COD_VRS_VET):
        V = aliased(tables.VersionEtape)
        IAE = aliased(tables.InsAdmEtp)
        session = self.getSession()
        recherche = session.query(V.LIB_WEB_VET, func.concat(V.COD_ETP + "-", V.COD_VRS_VET), func.count(distinct(IAE.COD_IND)).label("nb_etu")).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).filter(and_(V.COD_ETP == COD_ETP, V.COD_VRS_VET == int(COD_VRS_VET))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET)
        #session.close()
        return recherche.first()

    def getInfosELP(self, COD_ELP):
        ELP = aliased(tables.ElementPedagogi)
        ICE = aliased(tables.IndContratElp)
        session = self.getSession()
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(self.cod_anu))).filter(ELP.COD_ELP == COD_ELP).group_by(ELP.LIB_ELP, ELP.COD_ELP)
        #session.close()
        return recherche.first()

    def getInfosGPE(self, COD_GPE):
        GPE = aliased(tables.Groupe)
        IAG = aliased(tables.IndAffecteGpe)
        session = self.getSession()
        recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu"), GPE.COD_EXT_GPE).outerjoin(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(self.cod_anu))).filter(GPE.COD_GPE == int(COD_GPE)).group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE)
        #session.close()
        return recherche.first()

    def getInscriptionPedago(self, COD_ETU, COD_ETP, COD_VRS_VET):
        ICE = aliased(tables.IndContratElp)
        IND = aliased(tables.Individu)
        ELP = aliased(tables.ElementPedagogi)
        session = self.getSession()
        recherche = session.query(ICE.COD_ELP, ELP.LIB_ELP).outerjoin(IND, ICE.COD_IND==IND.COD_IND).outerjoin(ELP, ICE.COD_ELP==ELP.COD_ELP).filter(and_(ICE.COD_ANU==int(self.cod_anu), ICE.COD_ETP == COD_ETP, ICE.COD_VRS_VET == int(COD_VRS_VET), IND.COD_ETU==int(COD_ETU)))
        #session.close()
        return recherche.all()

    def getToutesInscriptionPedago(self):
        ICE = aliased(tables.IndContratElp)
        IND = aliased(tables.Individu)
        ELP = aliased(tables.ElementPedagogi)
        session = self.getSession()
        recherche = session.query(ICE.COD_IND, ICE.COD_ELP).outerjoin(IND, ICE.COD_IND==IND.COD_IND).outerjoin(ELP, ICE.COD_ELP==ELP.COD_ELP).filter(ICE.COD_ANU==int(self.cod_anu))
        #session.close()
        return recherche.all()

    def getUeEtape(self, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        requete = text("""SELECT ere.cod_elp_fils, elp.lib_elp
                          FROM elp_regroupe_elp ere, element_pedagogi elp
                          WHERE elp.cod_elp = ere.cod_elp_fils
                          START WITH ere.cod_lse in
                             (SELECT LSE.COD_LSE
                             FROM LISTE_ELP LSE, VET_REGROUPE_LSE VRL
                             WHERE vrl.cod_etp = '%s'
                                AND vrl.cod_vrs_vet = %s
                                AND lse.cod_lse = vrl.cod_lse
                                AND vrl.dat_frm_rel_lse_vet is null
                                AND lse.eta_lse != 'F'
                             )
                             AND ere.cod_elp_pere is null
                             AND ere.eta_elp_fils != 'F'
                             AND ere.tem_sus_elp_fils = 'N'
                          CONNECT BY PRIOR ere.cod_elp_fils = ere.cod_elp_pere
                             AND ere.eta_elp_fils != 'F'
                             AND ere.tem_sus_elp_fils = 'N'
                             AND NVL (ere.eta_elp_pere, 'O') != 'F'
                             AND NVL (ere.tem_sus_elp_pere, 'N') = 'N'
                             AND ere.eta_lse != 'F'
                             AND ere.date_fermeture_lien is null
                      """ % (str(COD_ETP), int(COD_VRS_VET)))
        recherche = session.execute(requete)
        #session.close()
        return recherche.fetchall()

    def getCodAnu(self):
        return self.cod_anu

    def getSession(self):
        try:
            self.getBind()
        except:
            self.sessionApogee = None
        if not self.sessionApogee:
            #print "add session"
            try:
                self.Session.close()
            except:
                pass
            engine = create_engine(self.url_connexion, echo=True)
            self.Session.configure(bind=engine)
            self.sessionApogee = "config"
        #print "return session"
        return self.Session()

    def getURLApogee(self):
        return self.url_connexion

    def getVersionEtape(self, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        VET = aliased(tables.VersionEtape)
        etape = session.query(VET.LIB_WEB_VET).filter(and_(VET.COD_ETP==COD_ETP, VET.COD_VRS_VET==COD_VRS_VET)).first()
        #session.close()
        return etape

    security.declarePrivate('convertirDate')

    def convertirDate(self, d, us=False):
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m-%d")

    def rechercherEtape(self, listeRecherche):
        listeCond = []
        V = aliased(tables.VersionEtape)
        VV = aliased(tables.VdiFractionnerVet)
        IAE = aliased(tables.InsAdmEtp)
        for element in listeRecherche:
            mot = self.supprimerAccent(element).upper()
            listeCond.append(or_(func.upper(V.COD_ETP).like(mot), func.upper(V.LIB_WEB_VET).like(mot)))
        session = self.getSession()
        recherche = session.query(V.LIB_WEB_VET, func.concat(V.COD_ETP + "-", V.COD_VRS_VET), VV.DAA_FIN_RCT_VET, func.max(VV.DAA_FIN_VAL_VET), func.count(distinct(IAE.COD_IND)).label("nb_etu")).outerjoin(VV, and_(VV.COD_ETP==V.COD_ETP, VV.COD_VRS_VET==V.COD_VRS_VET)).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).filter(and_(VV.DAA_FIN_RCT_VET >= int(self.cod_anu), VV.DAA_FIN_VAL_VET >= int(self.cod_anu), and_(*listeCond))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET, VV.DAA_FIN_RCT_VET).having(func.count(distinct(IAE.COD_IND)) > 0).order_by(V.LIB_WEB_VET)
        return recherche.all()

    def rechercherToutesEtapes(self):
        V = aliased(tables.VersionEtape)
        VV = aliased(tables.VdiFractionnerVet)
        IAE = aliased(tables.InsAdmEtp)
        session = self.getSession()
        recherche = session.query(V.LIB_WEB_VET, func.concat(V.COD_ETP + "-", V.COD_VRS_VET), VV.DAA_FIN_RCT_VET, func.max(VV.DAA_FIN_VAL_VET), func.count(distinct(IAE.COD_IND)).label("nb_etu")).outerjoin(VV, and_(VV.COD_ETP==V.COD_ETP, VV.COD_VRS_VET==V.COD_VRS_VET)).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).filter(and_(VV.DAA_FIN_RCT_VET >= int(self.cod_anu), VV.DAA_FIN_VAL_VET >= int(self.cod_anu))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET, VV.DAA_FIN_RCT_VET).having(func.count(distinct(IAE.COD_IND)) > 0).order_by(V.LIB_WEB_VET)
        return recherche.all()

    def rechercherELP(self, listeRecherche, uel):
        listeCond = []
        ELP = aliased(tables.ElementPedagogi)
        ERE = aliased(tables.ElpRegroupeElp)
        ICE = aliased(tables.IndContratElp)
        for element in listeRecherche:
            mot = self.supprimerAccent(element).upper()
            listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot)))
        if uel:
            listeCond.append(ERE.COD_LSE.like(self.uel + '%'))
        else:
            listeCond.append(~ERE.COD_LSE.like(self.uel + '%'))
        session = self.getSession()
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, ERE.COD_ELP_FILS==ELP.COD_ELP).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(self.cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', and_(*listeCond))).group_by(ELP.LIB_ELP, ELP.COD_ELP).having(func.count(distinct(ICE.COD_IND)) > 0).order_by(ELP.LIB_ELP)
        return recherche.all()

    def rechercherToutesELPs(self, uel=None):
        ELP = aliased(tables.ElementPedagogi)
        ERE = aliased(tables.ElpRegroupeElp)
        ICE = aliased(tables.IndContratElp)
        if uel:
            condition = ERE.COD_LSE.like(self.uel + '%')
        else:
            condition = ~ERE.COD_LSE.like(self.uel + '%')
        session = self.getSession()
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, ERE.COD_ELP_FILS==ELP.COD_ELP).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(self.cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', condition)).group_by(ELP.LIB_ELP, ELP.COD_ELP).having(func.count(distinct(ICE.COD_IND)) > 0).order_by(ELP.LIB_ELP)
        return recherche.all()

    def rechercherGPE(self, listeRecherche):
        listeCond = []
        GPE = aliased(tables.Groupe)
        IAG = aliased(tables.IndAffecteGpe)
        for element in listeRecherche:
            mot = self.supprimerAccent(element).upper()
            listeCond.append(or_(func.upper(GPE.COD_EXT_GPE).like(mot), func.upper(GPE.LIB_GPE).like(mot)))
        session = self.getSession()
        recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu")).outerjoin(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(self.cod_anu))).filter(and_(GPE.LIB_GPE <> 'None', and_(*listeCond))).group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE).having(func.count(distinct(IAG.COD_IND)) > 0).order_by(GPE.LIB_GPE)
        return recherche.all()

    def rechercherTousGPEs(self):
        GPE = aliased(tables.Groupe)
        IAG = aliased(tables.IndAffecteGpe)
        session = self.getSession()
        recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu")).outerjoin(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(self.cod_anu))).filter(GPE.LIB_GPE <> 'None').group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE).having(func.count(distinct(IAG.COD_IND)) > 0).order_by(GPE.LIB_GPE)
        return recherche.all()

    def rechercherEtudiants(self, code, type):
        # à modifier uel
        session = self.getSession()
        IND = aliased(tables.Individu)
        if type == "etape":
            COD_ETP, COD_VRS_VET = code.split("-")
            IAE = aliased(tables.InsAdmEtp)
            recherche = session.query(IAE.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU).outerjoin(IND, IND.COD_IND==IAE.COD_IND).filter(and_(IAE.COD_ETP==COD_ETP, IAE.COD_VRS_VET==COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
        if type in ["ue", "uel"]:
            COD_ELP = code
            ICE = aliased(tables.IndContratElp)
            recherche = session.query(ICE.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU).outerjoin(IND, IND.COD_IND==ICE.COD_IND).filter(and_(ICE.COD_ELP==COD_ELP, ICE.COD_ANU==int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
        if type == "groupe":
            COD_GPE = code
            IAG = aliased(tables.IndAffecteGpe)
            recherche = session.query(IAG.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU).outerjoin(IND, IND.COD_IND==IAG.COD_IND).filter(and_(IAG.COD_GPE==COD_GPE, IAG.COD_ANU==int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
        return recherche.all()

    def exporterApogee(self, type="etape"):
        print "----------------------------------------------------"
        homeFS = "/Users/firos/Desktop/Formations"
        if type == "etape":
            exportJSON = self.rechercherToutesEtapes()
            nameFile = "exportEtape.json"
            #"""
            dicoJSON = {}
            num = 1
            for ligne in exportJSON:
                COD_ETP, COD_VRS_VET = ligne[1].split("-")
                print "%s : %s" % (str(num), ligne[1])
                num = num + 1
                recherche = self.getUeEtape(COD_ETP, COD_VRS_VET)
                if recherche: 
                    dicoJSON[ligne[1]] = recherche
                    print "%s : ok" % ligne[1]
                    break
            if dicoJSON:
                fichier = open("%s/exportUEsEtape.json" % homeFS, "wb")
                json.dump(dicoJSON, fichier, encoding="utf-8")
                fichier.close()
            #"""
        if type == "ue":
            exportJSON = self.rechercherToutesELPs()
            nameFile = "exportUE.json"
        if type == "uel":
            exportJSON = self.rechercherToutesELPs("uel")
            nameFile = "exportUEL.json"
        if type == "groupe":
            exportJSON = self.rechercherTousGPEs()
            nameFile = "exportGroupe.json"
            recherche = self.getTousEtudiantsGroupes()
            dicoJSON = {}
            for ligne in recherche:
                if not ligne[0] in dicoJSON:
                    dicoJSON[ligne[0]] = {"code": ligne[1], "etudiants": [ligne[-1]]}
                else:
                    dicoJSON[ligne[0]]["etudiants"].append(ligne[-1])
            if dicoJSON:
                fichier = open("%s/exportEtudiantsGroupe.json" % homeFS, "wb")
                json.dump(dicoJSON, fichier, encoding="utf-8")
                fichier.close()
        if type == "pedago":
            recherche = self.getToutesInscriptionPedago()
            nameFile = "exportPedago.json"
            exportJSON = {}
            for ligne in recherche:
                if not ligne[0] in exportJSON:
                    exportJSON[ligne[0]] = [ligne[1]]
                else:
                    exportJSON[ligne[0]].append(ligne[1])

        fichier = open("%s/%s" % (homeFS, nameFile), "wb")
        json.dump(exportJSON, fichier, encoding="utf-8")
        fichier.close()

    def importerApogee(self, type="etape"):
        homeFS = "/Users/firos/Desktop/Formations"
        dico = {"etape": "exportEtape.json"
               ,"ue"      : "exportUE.json"
               ,"uel"     : "exportUEL.json"
               ,"groupe"  : "exportGroupe.json"
               ,"pedago"  : "exportPedago.json"
               ,"ueetape" : "exportUEsEtape.json"
               }
        fichier = open("%s/%s" % (homeFS, dico[type]), "r")
        data = json.load(fichier, encoding="utf-8")
        fichier.close()
        if type == "pedago":
            len(data.keys())
        return len(data)

    def supprimerAccent(self, ligne):
        """ supprime les accents du texte source """
        accents = { 'a': ['à', 'ã', 'á', 'â'],
                    'e': ['é', 'è', 'ê', 'ë'],
                    'c': ['ç'],
                    'i': ['î', 'ï'],
                    'u': ['ù', 'ü', 'û'],
                    'o': ['ô', 'ö'] }
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                ligne = ligne.replace(accented_char, char)
        return ligne
