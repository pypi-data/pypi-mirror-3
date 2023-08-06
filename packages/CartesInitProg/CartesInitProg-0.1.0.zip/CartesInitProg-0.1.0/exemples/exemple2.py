# -*- coding: utf-8 -*-

from Cartes import *

init_tas(1,"[C+P+T+K]")

#(* Les autres tas sont vides. Un tas vide est représenté par une chaîne de caractères vide notée en Ocaml "" *)
def sommet_rouge(tas):
    return sommet_coeur(tas) or sommet_carreau(tas) 

while tas_non_vide(1):
    if sommet_rouge(1):
        deplacer_sommet(1,2)
    else:
        deplacer_sommet(1,3)


