import os

couleurs = ['TREFLE', 'PIQUE', 'COEUR', 'CARREAU']

valeurs = ['1', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2']

for i in range(52):
    couleur = couleurs[i%4]
    valeur = valeurs[(i/4)]
    os.system('convert {0}.png {1}.gif'.format(i+1, couleur+valeur))
    
