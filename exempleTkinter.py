import tkinter as tk


def valider(): #fonction pour la methode d'un bouton
    try:
        nombre = float(entrée.get()) #entrée.get() permet de recuperer la valeur de l'entrée "entrée" dans une variable
        resultat_label.config(text=f'Résultat : {nombre * 2}') #label.config permet de modifier les propriété d'un label, ici on change son texte pour y mettre le résulat
    except ValueError:
        resultat_label.config(text='Erreur : Veuillez saisir un nombre valide.')

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Exemple Tkinter")
fenetre.minsize(400,400)

# Création du label "exemple tkinter"
exemple_label = tk.Label(fenetre, text="Exemple Tkinter") #déclaration d'un objet label (fenetre est son parent, le label est dans la fenetre appelé "fenetre")
exemple_label.pack() #affiche le label dans la page (3 méthodes possible pour placer les éléments, pack(), place(), grid())
#pack() place l'élément directement en dessous du dernier élément


labelNombre = tk.Label(fenetre, text="Saisir un nombre :")
labelNombre.place(x=150, y=100) #place() permet de placer un élément avec ces coordonnées

entrée = tk.Entry(fenetre)  #déclaraction d'une entré de texte
entrée.place(x=140, y=120)

# Création du bouton "Valider"
bouton_valider = tk.Button(fenetre, text="Valider", command=valider)  #le bouton à un attribut command, qui peut etre associé a une fonction (cette fonctio recupere la valeur de l'entré et la multplie par 2)
bouton_valider.place(x=175, y=145)

# Création du label pour afficher le résultat
resultat_label = tk.Label(fenetre, text="")
resultat_label.place(x=165, y=170)

# Lancement de la boucle principale
fenetre.mainloop()


