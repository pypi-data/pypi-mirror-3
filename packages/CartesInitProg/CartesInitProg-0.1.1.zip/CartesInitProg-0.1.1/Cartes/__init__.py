# -*- coding: utf-8 -*-

"""
Les principaux elements du Module Cartes
----------------------------------------
* init_tas : numero_tas * string -> unit
     init_tas(num_tas,chaine) : initialise le tas num_tas
     avec la description donnee par chaine.
* deplacer_sommet : numero_tas * numero_tas -> unit
     deplacer_sommet(num_tas1,num_tas2) :  deplace la carte au
     sommet du tas num_tas1 vers le tas num_tas2.
* tas_vide : numero_tas -> bool
     tas_vide(num_tas) = vrai si le tas num_tas est vide, faux sinon.
* tas_non_vide : numero_tas -> bool
     tas_non_vide(num_tas) = vrai si le tas num_tas n'est pas vide,
     faux sinon.
* couleur_sommet : numero_tas -> couleur
     couleur_sommet(num_tas) = couleur au sommet du tas num_tas.
* sommet_trefle : numero_tas -> bool
     sommet_trefle(num_tas) = vrai si la carte au sommet du tas num_tas
     est un trefle, faux sinon.
* sommet_carreau : numero_tas -> bool
     sommet_carreau(num_tas) = vrai si la carte au sommet du tas num_tas
     est un carreau, faux sinon.
* sommet_coeur : numero_tas -> bool
     sommet_coeur(num_tas) = vrai si la carte au sommet du tas num_tas
     est un coeur, faux sinon.
* sommet_pique : numero_tas -> bool
     sommet_pique(num_tas) = vrai si la carte au sommet du tas num_tas
     est un pique, faux sinon.
* superieur : numero_tas * numero_tas -> bool
     superieur(num_tas1,num_tas2) = vrai si la carte au sommet
     du tas num_tas1 est superieure ou egale a celle du tas num_tas2,
     faux sinon.
* Admin.repare : unit -> unit
     repare l'automate lorsqu'il est casse.

"""


from Cartes.core import Core
from Cartes.core import Etat
from Cartes.model import *
from Cartes.ui import *


__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 14 18:08:41 2012'


__all__ = [
    'COEUR', 'CARREAU', 'PIQUE', 'TREFLE',
    'init_tas',
    'deplacer_sommet',
    'couleur_sommet',
    'tas_vide',
    'tas_non_vide',
    'sommet_trefle',
    'sommet_pique',
    'sommet_coeur',
    'sommet_carreau',
    'superieur',
    'affichage_en_mode_graphique',
    'affichage_en_mode_texte',
    'affichage_en_mode_texte_et_graphique',
    'fixer_delai',
    'pause'
]


CORE = Core(Etat(), Delai())


# Cartes' API from OO to procedural

pause = CORE.pause
init_tas = CORE.init_tas
deplacer_sommet = CORE.deplacer_sommet
maj_affichage = CORE.maj_affichage
couleur_sommet = CORE.couleur_sommet
tas_vide = CORE.tas_vide
tas_non_vide = CORE.tas_non_vide
sommet_trefle = CORE.sommet_trefle
sommet_pique = CORE.sommet_pique
sommet_coeur = CORE.sommet_coeur
sommet_carreau = CORE.sommet_carreau
superieur = CORE.superieur
affichage_en_mode_texte = CORE.affichage_en_mode_texte
affichage_en_mode_graphique = CORE.affichage_en_mode_graphique
affichage_en_mode_texte_et_graphique = CORE.affichage_en_mode_texte_et_graphique
fixer_delai = CORE.fixer_delai

# eof
