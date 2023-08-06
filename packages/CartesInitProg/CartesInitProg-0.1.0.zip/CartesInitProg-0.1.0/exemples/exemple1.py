# -*- coding: utf-8 -*-

from Cartes import *

##affichage_en_mode_graphique()
#affichage_en_mode_texte()
#affichage_en_mode_texte_et_graphique()
##
init_tas(1,"CPCP")

#(* Les autres tas sont vides. Un tas vide est représenté par une chaîne de caractères vide notée en Ocaml "" *)
init_tas(2,"")
affichage_en_mode_texte()
fixer_delai(0.5)
init_tas(3,"")
init_tas(4,"")
#(* Nous savons que la carte du dessus est un Pique, donc va sur le tas 2 *)
deplacer_sommet(1,2)
#(* La suivante est un coeur *)
deplacer_sommet(1,3)
#(* La suivante est un pique *)
deplacer_sommet(1,2)
#(* La dernière est un coeur *)
affichage_en_mode_graphique()

deplacer_sommet(1,3)

