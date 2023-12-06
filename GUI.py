from typing import Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pynetlogo
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from matplotlib.animation import FuncAnimation
import threading
import _sqlite3
import re
import time
import schedule
from datetime import datetime
import ctypes
import numpy as np
import mplcursors




#création de la fenetre principale
class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()
        

        self.title("App MES")
        self.state('zoomed')
        self.minsize(600, 300)
        ctypes.windll.shcore.SetProcessDpiAwareness(1) #pour la résolution de l'écran
        self.protocol("WM_DELETE_WINDOW", lambda:self.fermeture_application()) #conservation du temps dans la bdd a la fermeture de l'app

        self.netlogo = pynetlogo.NetLogoLink(gui=True)
        self.netlogo.load_model('./Alpha.nlogo')  # Accéder à netlogo depuis la GUI
        self.netlogo.command('setup')

        self.menu = Menu(self, self.netlogo)
        self.menu.pack(fill="both", expand=True)  # Ajoutez cette ligne pour afficher le widget Menu
        
        self.boucle_principale() #qui permet de verifier si l'on doit réaliser un ordre a cette heure ci

        self.mainloop()

        
    def fermeture_application(self):
        print("def fermeture app")
        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsConserve = self.c.fetchone()
    
        self.c.execute("UPDATE tempsMachine SET tempsconserve = ?", tempsConserve)
        self.conn.commit()
        self.destroy()

    def boucle_principale(self):
        # Ajoutez ici le code que vous souhaitez exécuter périodiquement
        #print("5s")
        
        now = datetime.now().time()

        if now.hour == 12 and now.minute == 17:
            print("Il est l'h")
            self.menu.page1.playingState()
            self.menu.page1.playMethod(self.netlogo)
            self.menu.page1.prodA(self.netlogo)
       
        # Planifiez la prochaine itération de la boucle après 5000 millisecondes (5 secondes)
        if(self.menu.page1.playing == False):
            self.after(5000, self.boucle_principale)
    
    
    

#menu en au de l'écran
class Menu(ttk.Notebook):
    def __init__(self, parent, netlogo):
        super().__init__(parent)

        self.page2 = Dashboard(self)
        self.page3 = Dashboard2(self)
        self.page4 = Dashboard3(self)
        self.page5 = Order(self)
        self.page1 = PanneauDeControle(self, netlogo, self.page2, self.page3, self.page4)

        self.add(self.page1, text ='Panneau de controle') 
        self.add(self.page2, text ='out1')
        self.add(self.page3, text = 'out2')
        self.add(self.page4, text = 'out3')
        self.add(self.page5, text='Ordre de commande')
        

#page du panneau de controle
class PanneauDeControle(ttk.Frame):
    def __init__(self, parent, netlogo, dashboard, dashboard2, dashboard3):
        super().__init__(parent)
        #connexion BDD
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()
        self.playing = False
        self.dashboard = dashboard
        self.dashboard2 = dashboard2
        self.dashboard3 = dashboard3
        self.compteur = 0
        self.detailWindow = 0          #fenetreDétail créée quand appui bouton
        self.preSimulatedTime = 0
        schedule.every(10).seconds.do(self.ma_fonction)

        #récupere le temps totalConservé à l'initialisation (le temps conservé est le temps total pendant laqual l'app à été played)
        self.c.execute("SELECT tempsConserve FROM tempsMachine ORDER BY id DESC LIMIT 1")
        totalTimeTuple = self.c.fetchone()
        self.totalTime = totalTimeTuple[0]
        print("tempsConservé = " + str(totalTimeTuple))
        
        style = ttk.Style()
        style.configure('Red.TFrame', background='#34568B')
        
        # Appliquez le style à la frame
        self.configure(style='Red.TFrame')

        self.buttonPlay = ttk.Button(self, text= "Lancer simulation",command=lambda: [self.playingState(), self.playMethod(netlogo)])
        self.buttonPlay.grid(row=0, column=0,padx= 50, pady=50)

        self.buttonA = ttk.Button(self, text="A", command= lambda: self.prodA(netlogo))
        self.buttonA.grid(row=1, column=0,padx= 50, pady=(0,50))

        self.buttonI = ttk.Button(self, text="I", command= lambda: self.prodI(netlogo))
        self.buttonI.grid(row=2, column=0,padx= 50, pady=(0,50))

        self.buttonP = ttk.Button(self, text="P", command= lambda: self.prodP(netlogo))
        self.buttonP.grid(row=3, column=0,padx= 50, pady=(0,50))

        self.buttonB = ttk.Button(self, text="B", command= lambda: self.prodB(netlogo))
        self.buttonB.grid(row=4, column=0,padx= 50, pady=(0,50))

        self.buttonE = ttk.Button(self, text="E", command= lambda: self.prodE(netlogo))
        self.buttonE.grid(row=5, column=0,padx= 50, pady=(0,50))

        self.buttonL = ttk.Button(self, text="L", command= lambda: self.prodL(netlogo))
        self.buttonL.grid(row=6, column=0,padx= 50, pady=(0,50))

    #lance la prod de la lettre A (crée dans la bdd une ligne pour les tables: lettre, opération et lettretemps)
    def prodA(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'A'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "A" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)
            #recupere le simulated time au lancement de la lettre
            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            #print(str((re.search(r'\d+', str(resultID))).group()))
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'A', 'en cours'))
        
    def prodI(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'I'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "I" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)

            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'I', 'en cours'))

    def prodP(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'P'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "P" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)

            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'P', 'en cours'))

    def prodB(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'B'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "B" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)

            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'B', 'en cours'))

    def prodE(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'E'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "E" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)

            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'E', 'en cours'))

    def prodL(self, netlogo):
        if netlogo.report("time-for-possible-launching") == 0:
            lettre = 'L'
            netlogo.command('if Time-for-Possible-launching = 0 [create.product "L" set Time-for-Possible-launching 300]')
            last_product_who = max(netlogo.report("[who] of products"))
            self.c.execute("INSERT INTO lettre (lettre, netlogoID, numeroEtape, fini, graphAdd) VALUES (?,?,?,?,?)", (lettre, last_product_who, 0, "en cours","no"))
            self.c.execute("SELECT id FROM lettre ORDER BY id DESC LIMIT 1") #recupere l'id de la lettre
            resultID = self.c.fetchone()
            self.c.execute("INSERT INTO operation (lettre_id) VALUES (?)", resultID)

            tempsDebut = netlogo.report("simulated.time")
            self.c.execute("INSERT INTO lettreTemps (lettre_id, tempsDebut) VALUES (?, ?)", (resultID[0], tempsDebut))

            self.conn.commit()
            self.dashboard3.tableauLettre.insert("",0,iid= int((re.search(r'\d+', str(resultID))).group()),values=(str((re.search(r'\d+', str(resultID))).group()),'L', 'en cours'))


    #methode la plus importante, qui réaliser chaque boucle et recupere les différente donnée tout les x tics, et update les graph du dashboard a la fin 
    def playMethod(self, netlogo):
        #schedule.run_pending()

        
        
        if self.playing == True:
            
            netlogo.repeat_command('go', 1)
            self.compteur+=1
            self.master.master.after(1, lambda :self.playMethod(netlogo))

            #tout les 20 tic
            if (self.compteur % 20)== 0:
                self.UpdateTotalTime(netlogo) #mise a jours du temps total dans la bdd
                
                simulatedTime = netlogo.report("simulated.time")
                if(simulatedTime == self.preSimulatedTime + 1200):
                    self.preSimulatedTime = simulatedTime
                    self.dashboard.updateHistogramme()
                    self.dashboard.updateAvg()

                #si il y a des produit, on récuperer leur attribut WHO pour récuperer leurs ID de la BDD. puis on récuperer ou modifie les donnée en fonction de leur ID
                if netlogo.report('any? products'):
                    productsWho = netlogo.report("[who] of products")
                    for i in range(len(productsWho)):
                        if netlogo.report("[product.state] of product" + " " + str(productsWho[i])) == "Waiting":
                            machine = netlogo.report("[heading.workstation] of product" + " " + str(productsWho[i]))
                            operation = netlogo.report("[next.product.operation] of product" + " " + str(productsWho[i]))
                            #print("machine" + str(machine) + "et opération" + str(operation))

                            self.c.execute("SELECT id FROM lettre WHERE netlogoID = ? ORDER BY id DESC LIMIT 1", (productsWho[i],)) #recupere l'id de la lettre
                            resultID = self.c.fetchone()
                            #print(resultID)

                            self.c.execute("SELECT numeroEtape FROM lettre WHERE id = ?", resultID)
                            etapePrecedente = self.c.fetchone()
                            #print("étape précédente = " + str(etapePrecedente[0]))
                            
                            numEtapeEnCours = int(netlogo.report("[currentsequenceorder] of product" + " " + str(int(productsWho[i])))) + 1
                            #print("étape: " + str(numEtapeEnCours))
                            resultID = int((re.search(r'\d+', str(resultID))).group())
                            
                            if(etapePrecedente[0] != int(numEtapeEnCours)):
                                print("machine" + str(machine) + "et opération" + str(operation))
                                print("étape précédente = " + str(etapePrecedente[0]))
                                
                                requete = "UPDATE operation SET etape0" + str(numEtapeEnCours) + " " + "= ? WHERE lettre_id = ?"
                                self.c.execute(requete, ((str(operation)+"-" + str(machine)), resultID))

                                self.c.execute("SELECT temps" + str(machine) + " " +"FROM tempsMachine ORDER BY id DESC LIMIT 1")
                                machineTimeBDD = self.c.fetchone()
                                #print("str de machine =" + str(machine))
                                newMachineTime = machineTimeBDD[0] + self.getMachineOperationTime(machine)
                                self.dashboard.updateGantt(machine)
                                
                                #self.c.execute("UPDATE tempsMachine SET temps" + str(machine) + " " +"= ? WHERE id = (SELECT MAX(id) FROM tempsMachine", (newMachineTime,))
                                self.c.execute("UPDATE tempsMachine SET temps" + str(machine) + " = ? WHERE id = (SELECT MAX(id) FROM tempsMachine)", (newMachineTime,))


                            self.c.execute("UPDATE lettre SET numeroEtape = ? WHERE id = ?", (numEtapeEnCours, resultID))
                            self.conn.commit()
                                
                            if(etapePrecedente[0] != int(numEtapeEnCours)):
                            
                                if (str(operation) == "O9"):
                                        selectedItem = int((re.search(r'\d+', str(resultID))).group())
                                        self.dashboard3.tableauLettre.item(selectedItem, values=(self.dashboard3.tableauLettre.item(selectedItem, 'values')[0], self.dashboard3.tableauLettre.item(selectedItem, 'values')[1], 'terminé'))
                                        self.c.execute("UPDATE lettre SET fini = ? WHERE id = ?", ("terminé", resultID))
                                        #print("condition opé5 validé")
                                        tempsFin = netlogo.report("simulated.time")
                                        self.c.execute("UPDATE lettreTemps SET tempsFin = ? WHERE lettre_id = ?", (tempsFin, resultID))
                                        
                                        self.c.execute("SELECT tempsDebut FROM lettreTemps WHERE lettre_id = ?", (resultID,))
                                        tempsDebut = self.c.fetchone()
                                        tempsTotal = tempsFin - tempsDebut[0]
                                        print('lopération a pris: '+ str(tempsTotal) + "s")

                                        #clacule OOE
                                        self.calculeOOE()

                                        self.c.execute("UPDATE lettre SET temps = ? WHERE id = ?", (tempsTotal, resultID))
                                        
                                        self.conn.commit()

                                        

                                   
                                    
    def ma_fonction(self):
        print("Code exécuté toutes les minutes")

                  
    #pas fini
    def buttonTimer(self, netlogo):
        styleBoutton = ttk.Style()
        styleBoutton.configure('MyRedButton.TButton', foreground='red')
        if netlogo.report("time-for-possible-launching") != 0:
            self.buttonA.configure(state="disabled",style="MyRedButton.TButton")
        else:
            self.buttonA.config(state="normal")

    #modifi l'attribut selfplaying lorsque 'lon appuie sur le bouton, si à False, la play methode ne fait rien (voir playMethod)
    def playingState(self):
        self.playing = not self.playing
        if self.playing == True:
            self.buttonPlay.config(text="Arreter la simulation")
        else:
            self.buttonPlay.config(text="Lancer la simulation")

    #update le temps total (tout les 20 tic, voir playMethod)
    def UpdateTotalTime(self, netlogo):
        simulatedTime = netlogo.report("simulated.time")
        
        totalTime = self.totalTime + int(simulatedTime)
        #print("tempsTotal =" +str(totalTime))
        self.c.execute("UPDATE tempsMachine SET tempsTotal = ?", (totalTime,))
        self.conn.commit()
        
    #renvoie le temps d'opération des différente machine dans la BDD
    def getMachineOperationTime(self, machine):
       
        if str(machine) == "M1":
            opeTime = 10
        elif str(machine) in ["M2", "M3", "M4", "M7"]:
            opeTime = 10
           
        elif str(machine) == "M5":
            opeTime = 5
           
        elif str(machine) == "M6":
            opeTime = 60
            
        else:
            print("no such machine")
            opeTime = 0
        return opeTime
         
    #réalise le calcule de l'OOE
    def calculeOOE(self): 
        self.c.execute("SELECT * FROM tempsMachine ORDER BY id DESC LIMIT 1")
        tempsMachine = self.c.fetchone()

        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        ooeMachine = [0] *7
        ooeMachine[0] = tempsMachine[3]/tempsTotal[0]
        ooeMachine[1] = tempsMachine[4]/tempsTotal[0]
        ooeMachine[2] = tempsMachine[5]/tempsTotal[0]
        ooeMachine[3] = tempsMachine[6]/tempsTotal[0]
        ooeMachine[4] = tempsMachine[7]/tempsTotal[0]
        ooeMachine[5] = tempsMachine[8]/tempsTotal[0]
        ooeMachine[6] = tempsMachine[9]/tempsTotal[0]

        print("tempsMachine" + str(ooeMachine))

    
        

#page dashboard
class Dashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()

        self.cursor = None
            
        self.initHistogramme()
        self.initAvg()
        self.initGantt()
        self.initGraph3()


    #initialise les graphs avec les info de la bdd
    def initHistogramme(self):
        # Récupération des temps depuis la base de données
        self.c.execute("SELECT * FROM tempsMachine ORDER BY id DESC LIMIT 1")
        tempsMachine = self.c.fetchone()

        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        # Extraction des temps des différentes machines
        temps_machines = tempsMachine[3:10]
        print("len de tempsMachine = " + str(len(temps_machines)))
        ooeMachine = [0]*7

        for x in range (len(ooeMachine)):
            ooeMachine[x] = (temps_machines[x]/tempsTotal[0]) *100
        
        print("ooe Machine="  + str(ooeMachine))

        # Création de l'histogramme
        self.fig, self.ax1 = plt.subplots(figsize=(4.8, 3.8))
    
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
       
        # Premier subplot (votre histogramme existant)
        self.ax1.bar(range(1, len(ooeMachine) + 1), ooeMachine)
        self.ax1.set_xlabel('Machines')
        self.ax1.set_ylabel('OOE%')
        self.ax1.set_title('temps utilisation machine/temps Production total')
        
        
        # Deuxième subplot vide
        self.c.execute("SELECT xTemps FROM graphAvg")
        x = self.c.fetchall()
        self.c.execute("SELECT yAvg FROM graphAvg")
        y = self.c.fetchall()

        # Affichage de l'histogramme dans la fenêtre principale
        self.canvas = tk.Canvas(self, width=800, height=500)
        self.canvas.place(x=850, y=25)
        self.fcanvas = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.fcanvas.draw()
        self.fcanvas.get_tk_widget().pack()

    #methode qui permet d'update le graph (voir fin playMethod du panneau de controle)
    def updateHistogramme(self):
        # Récupération des temps depuis la base de données
        self.c.execute("SELECT * FROM tempsMachine ORDER BY id DESC LIMIT 1")
        tempsMachine = self.c.fetchone()

        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        # Extraction des temps des différentes machines
        temps_machines = tempsMachine[3:10]
        print("len de tempsMachine = " + str(len(temps_machines)))
        ooeMachine = [0] * 7

        for x in range(len(ooeMachine)):
            ooeMachine[x] = (temps_machines[x] / tempsTotal[0]) * 100

        # Mise à jour des données de l'histogramme existant
        self.ax1.clear()
        self.ax1.bar(range(1, len(ooeMachine) + 1), ooeMachine)
        self.ax1.set_xlabel('Machines')
        self.ax1.set_ylabel('OOE%')
        self.ax1.set_title('temps utilisation machine/temps Production total')

    
        print("Graph mis à jour")

    def initAvg(self):

        self.c.execute("SELECT xTemps FROM graphAvg")
        x = self.c.fetchall()
        self.c.execute("SELECT yAvg FROM graphAvg")
        y = self.c.fetchall()

        self.figAvgTime, self.ax2 = plt.subplots(figsize=(4.8, 3.8))
        
        self.figAvgTime.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)

        self.ax2.set_title('Temps Moyen lettres (tout les 1200 st)')
        self.ax2.plot(x, y, marker='o', linestyle=' ', color= 'blue')
        self.ax2.set_xlabel('tempsTotal')
        self.ax2.set_ylabel("Temps moyen d'une lettre")

        #mplcursors.cursor(self.ax2, hover=True, bbox=dict(boxstyle="square,pad=0.5", facecolor="white", edgecolor="#ddd")).connect("add", lambda sel: sel.annotation.set_text(f"({sel.target[0]}, {sel.target[1]})"))
        self.cursor = mplcursors.cursor(
            self.ax2,
            hover=True,
            annotation_kwargs=dict(
                bbox=dict(
                    facecolor="white",
                    edgecolor="#ddd",
                ),
            )
        ).connect("add", lambda sel: sel.annotation.set_text(f"({sel.target[0]}, {sel.target[1]})"))

        
        # Affichage de l'histogramme dans la fenêtre principale
        self.canvasAvg = tk.Canvas(self, width=800, height=500)
        self.canvasAvg.place(x=1375, y=25)
        self.fcanvasAvg = FigureCanvasTkAgg(self.figAvgTime, master=self.canvasAvg)
        self.fcanvasAvg.draw()
        self.fcanvasAvg.get_tk_widget().pack()

    def updateAvg(self):
        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        self.c.execute("SELECT temps FROM lettre WHERE graphAdd = ? AND temps IS NOT NULL", ("no",))
        resultats = self.c.fetchall()
        self.c.execute("UPDATE lettre SET graphAdd = ? WHERE graphAdd = ? AND temps IS NOT NULL", ("yes", "no"))
        self.conn.commit()

        # Calcul de la moyenne des temps
        if resultats:
            temps_moyen = sum(row[0] for row in resultats) / len(resultats)
            print("Moyenne des temps des 5 dernières lettres :", temps_moyen)
        else:
             print("Aucune lettre trouvée dans la base de données.")
        
        x = tempsTotal[0]  
        y = temps_moyen
        self.ax2.plot(x, y, marker='o', linestyle='-', color= 'blue')
        # Rafraîchissement de l'affichage de l'histogramme
        self.fcanvasAvg.draw()

        self.cursor.remove()
        
        self.cursor = mplcursors.cursor(
            self.ax2,
            hover=True,
            annotation_kwargs=dict(
                bbox=dict(
                    facecolor="white",
                    edgecolor="#ddd",
                ),
            )
        ).connect("add", lambda sel: sel.annotation.set_text(f"({sel.target[0]}, {sel.target[1]})"))
        
        self.c.execute("INSERT INTO graphAvg (xTemps, yAvg) VALUES(?,?)", (tempsTotal[0], temps_moyen))
        self.conn.commit()

    def initGantt(self):
        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        self.figGantt, self.axGantt = plt.subplots(figsize=(10, 4))
        self.axGantt.set_xlim(tempsTotal[0] - 200, tempsTotal[0] + 200)
        #crée 7 lignes pour chacune des machines
        self.axGantt.barh(y="M1", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M2", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M3", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M4", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M5", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M6", width=0, left=tempsTotal[0])
        self.axGantt.barh(y="M7", width=0, left=tempsTotal[0])
        self.axGantt.set_xlabel('Simulated Time')
        self.axGantt.set_ylabel('Machines')
        self.axGantt.set_title('gantt Machine')

        self.canvasGantt = tk.Canvas(self, width=400, height=400)
        self.canvasGantt.place(x=850, y=450)
        self.fcanvasGantt = FigureCanvasTkAgg(self.figGantt, master=self.canvasGantt)
        
        self.fcanvasGantt.draw()
        self.fcanvasGantt.get_tk_widget().pack()


    def updateGantt(self, machine):

        self.c.execute("SELECT tempsTotal FROM tempsMachine")
        tempsTotal = self.c.fetchone()

        print("entré dans updateGantt avec tempsTotal = " + str(tempsTotal[0]))

        if str(machine) == "M1":
            self.axGantt.set_xlim(tempsTotal[0] - 200, tempsTotal[0] + 200) #permet de recentrer l'axe x pour faire défiler le gantt
            self.axGantt.barh(y="M1", width=10, left=tempsTotal[0], color = 'blue')
            self.fcanvasGantt.draw()
            print("strMachine = " + str(machine))

        elif str(machine) in ["M2", "M3", "M4", "M7"]:
            self.axGantt.set_xlim(tempsTotal[0] - 200, tempsTotal[0] + 200)
            if str(machine) == "M2":
                self.axGantt.barh(y=str(machine), width=10, left=tempsTotal[0], color = 'purple')
            elif str(machine) == "M3":
                self.axGantt.barh(y=str(machine), width=10, left=tempsTotal[0], color = 'red')
            elif str(machine) == "M4":
                self.axGantt.barh(y=str(machine), width=10, left=tempsTotal[0], color = 'pink')
            elif str(machine) == "M4":
                self.axGantt.barh(y=str(machine), width=10, left=tempsTotal[0], color = 'yellow')

            self.fcanvasGantt.draw()
            print("strMachine = " + str(machine))

        elif str(machine) == "M5":
            self.axGantt.set_xlim(tempsTotal[0] - 200, tempsTotal[0] + 200)
            self.axGantt.barh(y=str(machine), width=5, left=tempsTotal[0])
            self.fcanvasGantt.draw()
            print("strMachine = " + str(machine))

        elif str(machine) == "M6":
            self.axGantt.set_xlim(tempsTotal[0] - 200, tempsTotal[0] + 200)
            self.axGantt.barh(y=str(machine), width=60, left=tempsTotal[0])
            self.fcanvasGantt.draw()
            print("strMachine = " + str(machine))
        else:
            print("no such machine")

    def initGraph3(self):
        
        self.fig3, self.ax3 = plt.subplots(figsize=(4.8, 3.8))
        self.fig3.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
        #crée 7 lignes pour chacune des machines
        self.ax3.barh(y="M1", width=0, left=0)
        self.ax3.barh(y="M2", width=0, left=0)
        self.ax3.barh(y="M3", width=0, left=0)
        self.ax3.barh(y="M4", width=0, left=0)
        self.ax3.barh(y="M5", width=0, left=0)
        self.ax3.barh(y="M6", width=0, left=0)
        self.ax3.barh(y="M7", width=0, left=0)
        self.ax3.set_xlabel('x')
        self.ax3.set_ylabel('y')
        self.ax3.set_title('soon')

        self.canvas3 = tk.Canvas(self, width=400, height=400)
        self.canvas3.place(x=325, y=25)
        self.fcanvas3 = FigureCanvasTkAgg(self.fig3, master=self.canvas3)
        
        self.fcanvas3.draw()
        self.fcanvas3.get_tk_widget().pack()
    

class Dashboard2(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()

class Dashboard3(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()

        #tableau des lettre
        self.tableauLettre = ttk.Treeview(self, columns=('lettre ID', 'lettre', 'en cours/terminé'),show='headings', selectmode='browse')
        self.tableauLettre.heading('lettre ID', text='lettre ID')
        self.tableauLettre.heading('lettre', text='lettre')
        self.tableauLettre.heading('en cours/terminé', text='en cours/terminé')

        self.tableauLettre.place(x=50, y=50)
        self.tableauLettre.column('lettre', width=200, anchor='center')
        self.tableauLettre.column('lettre ID', width=200, anchor='center')
        self.tableauLettre.column('en cours/terminé', width=200, anchor='center')

        #scrollbar
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.tableauLettre.yview)
        self.vsb.place(x=650, y=50, height=200+20)

        #menu "détail, qui s'affiche lors du clic droit quand un item du tableau est sélectionné"
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Détails", command= self.afficher_details)
        self.tableauLettre.bind("<Button-3>", self.afficher_menu_contextuel)

        #recupere les info de la BDD pour initialisé le tableau
        self.c.execute("SELECT id FROM lettre")
        self.resultIds = self.c.fetchall()
        self.c.execute("SELECT lettre FROM lettre")
        self.resultlettres = self.c.fetchall()
        #initialise le tableau
        for x in range(len(self.resultIds)):
            self.tableauLettre.insert("",0,int((re.search(r'\d+', str(self.resultIds[x]))).group()),values=(self.resultIds[x],self.resultlettres[x],'terminé'))

    #methoe qui affiche le bouton détail
    def afficher_menu_contextuel(self,event):
        selection = self.tableauLettre.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)

    #méthode qui se lance lors de l'appuie sur détail, il instancie simplement un objet de la classe détailLettre, est un autre page contenant les details
    def afficher_details(self):
        self.detailWindow = DetailLettre(self)


#page du détail des lettre du tableau
class DetailLettre(tk.Tk):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboardFrame = dashboard
        self.title("détail lettre")
        self.minsize(600, 400)

        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()
        
        iid = self.dashboardFrame.tableauLettre.selection()
        iid = iid[0]  #converti un tuple en un int

        self.c.execute("SELECT * FROM operation WHERE lettre_id = ?", (iid,))
        listeOperations = self.c.fetchone()

        #labeliid = ttk.Label(self, text=' '.join(listeOperations[2:9]))
        labeliid = ttk.Label(self, text='\n'.join(f'Opération {i+1}: {v}' for i, v in enumerate(listeOperations[2:11])))

        labeliid.pack()

        

class Order(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()
        #treeview des ordre de production
        self.nouvelleOrdrewindow = 0
        self.nouvelleOrdrebutton = ttk.Button(self, text='nouvelle ordre', command=lambda:self.creerNouvelleOrdre())
        self.nouvelleOrdrebutton.place(x=50,y=50)

        self.listeOrdre = ttk.Treeview(self, columns=('id', 'lettres', 'heure'),show='headings', selectmode='browse')
        self.listeOrdre.heading('id', text='id')
        self.listeOrdre.heading('lettres', text='lettres')
        self.listeOrdre.heading('heure', text='heure')
        self.listeOrdre.place(x=50, y=100)

        #treeview init
        self.c.execute("SELECT ordreID FROM ordrePlanifier")
        self.resultIds = self.c.fetchall()

        self.c.execute("SELECT lettres FROM ordrePlanifier")
        self.resultlettres = self.c.fetchall()

        self.c.execute("SELECT date FROM ordrePlanifier")
        self.resultdates = self.c.fetchall()

        
        for x in range(len(self.resultIds)):
            self.listeOrdre.insert("",0,int((re.search(r'\d+', str(self.resultIds[x]))).group()),values=(self.resultIds[x],self.resultlettres[x],self.resultdates[x]))

        #boutton modif/supp
        self.bMofif = ttk.Button(self, text='modifier')
        self.bMofif.place(x=700, y=160)
        self.bSupp = ttk.Button(self, text='supprimer', command=lambda: self.supprimerOrdreSelectionne())
        self.bSupp.place(x=700, y=225)

    def creerNouvelleOrdre(self):
        self.nouvelleOrdrewindow = NouvelleOrdre(self)

    def supprimerOrdreSelectionne(self):
        # Récupérer l'élément sélectionné
        selected_item = self.listeOrdre.selection()

        # Vérifier s'il y a un élément sélectionné
        if selected_item:
            # Supprimer l'élément sélectionné du treeview
            self.listeOrdre.delete(selected_item)
            #ne pas oublié de faire supp de la bdd

class NouvelleOrdre(tk.Tk):
    def __init__(self, order):
        super().__init__()
        self.orderFrame = order
        self.conn = _sqlite3.connect('BDDnetLogo.db')
        self.c = self.conn.cursor()
        #entrée des lettres de l'ordre de prod à planifier
        self.title("Nouvelle Odre de production")
        self.minsize(600, 400)

        self.labelLettre = ttk.Label(self, text='lettre')
        self.labelLettre.grid(row=0, column=0, padx=25, pady=25)

        self.lettreslist = ["A","I","P","B","E","L"]

        self.inputLetrre = ttk.Combobox(self, values= self.lettreslist, width=5)
        self.inputLetrre.grid(row=0, column=1, padx=0)

        self.labelX = ttk.Label(self, text="x")
        self.labelX.grid(row=0, column=2, padx=8)

        self.entryX = ttk.Entry(self, width=5)
        self.entryX.grid(row=0, column=3, padx=0)

        self.buttonAdd = ttk.Button(self, text="ajouté", command=lambda: self.ajoutLettreListe())
        self.buttonAdd.grid(row=0,column=4, padx=10)
        #treeview des lettre de l'ordre de prod
        self.listeLettreOrdre = ttk.Treeview(self, columns=('lettre', 'quantité'),show='headings', selectmode='browse')
        self.listeLettreOrdre.heading('lettre', text='lettre')
        self.listeLettreOrdre.heading('quantité', text='quantité')
        self.compteurlisteTreeview = 0

        self.listeLettreOrdre.place(x=75, y=100)
        #bouton planification heure
        self.labelPlanOrdre = ttk.Label(self, text='à')
        self.labelPlanOrdre.place(x=50, y=350)

        self.entryH = ttk.Entry(self, width=5)
        self.entryH.place(x=75, y=350)

        self.labelH = ttk.Label(self, text= "H")
        self.labelH.place(x=115, y=350)

        self.entryMin = ttk.Entry(self, width=5)
        self.entryMin.place(x=140, y=350)

        self.labelMin = ttk.Label(self, text="min")
        self.labelMin.place(x=185, y=350)

        self.boutonPlan = ttk.Button(self, text= "planifier", command= lambda: self.planifier())
        self.boutonPlan.place(x= 215, y=350)

    def ajoutLettreListe(self):
        self.compteurlisteTreeview += 1
        self.listeLettreOrdre.insert("",0,iid=self.compteurlisteTreeview,values=(self.inputLetrre.get(), self.entryX.get()))
        
    def planifier(self):

        result_string = ""

        for x in range(self.compteurlisteTreeview):
            lettreslx = self.listeLettreOrdre.item(x+1,'values')[0] * int(self.listeLettreOrdre.item(x+1, 'values')[1])
            result_string = result_string + lettreslx
            print(result_string)
        
        heure = self.entryH.get()
        minute = self.entryMin.get()
        print(heure + "H" + minute +"min")

        self.c.execute("INSERT INTO ordrePlanifier (lettres, date) VALUES (?,?)", (result_string, heure + "H" + minute +"min"))
        self.conn.commit()
        #self.c.execute("SELECT ordreID FROM ordrePlanifier ORDER BY id DESC LIMIT 1")
        self.c.execute("SELECT ordreID FROM ordrePlanifier ORDER BY ordreID DESC LIMIT 1")
        iid = self.c.fetchone()
        self.orderFrame.listeOrdre.insert("",0, iid=int((re.search(r'\d+', str(iid))).group()), values=(iid, result_string, (heure + "H" + minute +"min")))


    

monApp = Gui()