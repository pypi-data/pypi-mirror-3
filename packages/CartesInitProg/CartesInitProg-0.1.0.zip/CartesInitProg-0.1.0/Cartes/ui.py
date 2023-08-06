# -*- coding: utf-8 -*-

"""
User interface for the Carte package

- text based
- graphical (Tkinter)

"""


import glob
import os
import thread
import time
from Tkinter import *


__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Fri Jun 15 16:46:28 2012'


CARDHEIGHT = 96
CARDWIDTH = 72

PILEDIFF = CARDHEIGHT / 4
TASSEP = 30

HEIGHT = CARDHEIGHT * 6
WIDTH = CARDWIDTH * 4 + 3 * TASSEP

BASEDIR = os.path.dirname(__file__)


class AfficheurGraphique(object):

    afficheur = None

    def __init__(self, delai=None):
        default_delai = type('', (),{'valeur': 1})() 
        self.delai = delai or default_delai
    
    def threadmain(self):
        master = Tk()
        self.load_cards()
        self.canvas = Canvas(master, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        master.mainloop()

    def load_cards(self):
        self.cards_data = {}
        pattern = os.path.join(BASEDIR, 'images', '*.gif')
        for x in glob.glob(pattern):
            path, filename = os.path.split(x)
            key, ext = os.path.splitext(filename)
            self.cards_data[key] = PhotoImage(file=x)

    def affiche(self, etat):
        self.canvas.delete(ALL)
        for indice, tas in enumerate(etat.tas):
            for position, carte in enumerate(tas.cards):
                key = carte.couleur + str(carte.valeur)
                self.canvas.create_image(
                    indice*(CARDWIDTH + TASSEP),
                    HEIGHT - position * PILEDIFF,
                    image=self.cards_data[key], anchor = SW)
        time.sleep(self.delai.valeur)

    @classmethod
    def create(cls, delai):
        if cls.afficheur:
            return cls.afficheur    
        cls.afficheur = AfficheurGraphique(delai)
        thread.start_new_thread(cls.afficheur.threadmain, ())
        time.sleep(1)  # so the thread has initialized properly
        return cls.afficheur


class AfficheurTexte(object):

    def __init__(self, delai):
        self.delai = delai

    def affiche(self, etat):
        print etat
        print '----'

    @classmethod
    def create(cls, delai):
        return AfficheurTexte(delai)

# eof
