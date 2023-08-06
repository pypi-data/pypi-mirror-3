# -*- coding: utf-8 -*-

from Cartes import *

fixer_delai(.3)

init_tas(1,"[C+P+T+K]")

def sort(orig, dest, buf):
    """ trie le tas orig dans dest en utilisant buf comme tas temporaire
        Contrat d'utilisation: buf et dest vide
    """
    
    while tas_non_vide(orig):
        while tas_non_vide(orig):
            deplacer_sommet(orig, dest)
            if superieur(dest, orig):
                deplacer_sommet(dest, buf)
                deplacer_sommet(orig, dest)
            #else:
            #    deplacer_sommet(orig, buf)

        while tas_non_vide(buf):
            deplacer_sommet(buf, orig)

sort(1,2,3)
fixer_delai(3)
init_tas(4,"")
#pause("fini")
