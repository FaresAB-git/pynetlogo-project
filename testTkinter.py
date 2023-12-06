import tkinter as tk
from tkinter import ttk

# Fonction pour afficher les détails de l'élément sélectionné
def afficher_details():
    selection = treeview.selection()
    if selection:
        item = selection[0]
        # Récupérer les détails de l'élément (vous devrez adapter cela en fonction de vos données)
        details = treeview.item(item, 'values')

        # Créer une fenêtre pour afficher les détails
        details_window = tk.Toplevel(root)
        details_window.title("Détails de l'élément")
        details_label = tk.Label(details_window, text=details)
        details_label.pack()

# Fonction pour afficher le menu contextuel
def afficher_menu_contextuel(event):
    selection = treeview.selection()
    if selection:
        context_menu.post(event.x_root, event.y_root)

# Créer une fenêtre principale
root = tk.Tk()
root.title("Exemple de TreeView avec détails")

# Créer un TreeView
treeview = ttk.Treeview(root, columns=("Nom", "Âge"))
treeview.heading("Nom", text="Nom")
treeview.heading("Âge", text="Âge")

# Insérer des éléments dans le TreeView (vous devrez adapter cela avec vos données)
treeview.insert("", "end", values=("John", 30))
treeview.insert("", "end", values=("Jane", 25))

# Associer un menu contextuel
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Détails", command=afficher_details)

# Associer un gestionnaire d'événements pour le clic droit
treeview.bind("<Button-3>", afficher_menu_contextuel)

treeview.pack()

root.mainloop()

"""fig, ax = plt.subplots()
        ax.bar(range(1, len(ooeMachine) + 1), ooeMachine)
        ax.set_xlabel('Machines')
        ax.set_ylabel('OOE%')
        ax.set_title('temps utilisation machine/temps Production total')

        # Affichage de l'histogramme dans la fenêtre principale
        self.canvas = tk.Canvas(self, width=400, height=300)
        self.canvas.place(x=50, y=350)
        canvas = FigureCanvasTkAgg(fig, master=self.canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()"""