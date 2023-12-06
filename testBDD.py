import _sqlite3

conn = _sqlite3.connect('BDDnetLogo.db')

c = conn.cursor()

sql_create_lettre_table = """ CREATE TABLE IF NOT EXISTS lettre (
                                        id integer PRIMARY KEY,
                                        lettre text NOT NULL,
                                        netlogoID integer,
                                        temps integer,
                                        orderID integer,
                                        fini text,
                                        graphAdd text,
                                        numeroEtape integer,
                                        FOREIGN KEY (orderID) REFERENCES ordre (OrdreID)
                                    ); """



sql_create_operation_table = """CREATE TABLE IF NOT EXISTS operation (
                                    id integer PRIMARY KEY,
                                    lettre_id integer,
                                    etape01 text,
                                    etape02 text,
                                    etape03 text,
                                    etape04 text,
                                    etape05 text,
                                    etape06 text,
                                    etape07 text,
                                    etape08 text,
                                    etape09 text,
                                    etape010 text,
                                    FOREIGN KEY (lettre_id) REFERENCES lettre (id)
                                );"""

sql_create_lettreTemps_table = """ CREATE TABLE IF NOT EXISTS lettreTemps (
                                        lettre_id integer,
                                        tempsDebut integer,
                                        tempsFin integer,
                                        tempsTotal integer,
                                        FOREIGN KEY (lettre_id) REFERENCES lettre (id)
                                    ); """


sql_create_tempsMachine_table = """ CREATE TABLE IF NOT EXISTS tempsMachine (
                                        id integer PRIMARY KEY,
                                        tempsTotal integer,
                                        tempsConserve integer,
                                        tempsM1 integer,
                                        tempsM2 integer,
                                        tempsM3 integer,
                                        tempsM4 integer,
                                        tempsM5 integer,
                                        tempsM6 integer,
                                        tempsM7 integer
                                    ); """

sql_create_OOEMachine_table = """ CREATE TABLE IF NOT EXISTS ooeMachine (
                                        id integer PRIMARY KEY,
                                        ooeM1 integer,
                                        ooeM2 integer,
                                        ooeM3 integer,
                                        ooeM4 integer,
                                        ooeM5 integer,
                                        ooeM6 integer,
                                        ooeM7 integer
                                    ); """

sql_create_graphAvg_table = """ CREATE TABLE IF NOT EXISTS graphAvg (
                                        id integer PRIMARY KEY,
                                        xTemps integer,
                                        yAvg integer
                                    ); """


sql_create_odre_table = """CREATE TABLE IF NOT EXISTS ordre (
                                    ordreID integer,
                                    lettres text NOT NULL,
                                    date text,
                                    temps integer,
                                    FOREIGN KEY (ordreID) REFERENCES ordrePlanifier (ordreID)
                                );"""


sql_create_odrePlanifier_table = """CREATE TABLE IF NOT EXISTS ordrePlanifier (
                                    ordreID integer PRIMARY KEY,
                                    lettres text NOT NULL,
                                    date text
                                    
                                );"""

"""c.execute(sql_create_odrePlanifier_table)
c.execute(sql_create_odre_table)
c.execute(sql_create_operation_table)
c.execute(sql_create_lettre_table)
c.execute(sql_create_lettreTemps_table)
c.execute(sql_create_tempsMachine_table)
c.execute(sql_create_graphAvg_table)"""

#c.execute("INSERT INTO tempsMachine (tempsTotal,tempsConserve, tempsM1, tempsM2, tempsM3, tempsM4, tempsM5, tempsM6, tempsM7) VALUES (?,?,?,?,?,?,?,?,?)", (1,0,0,0,0,0,0,0,0,))
#c.execute("INSERT INTO graphAvg (xTemps, yAvg) VALUES(?,?)", (0, 800))

#c.execute("SELECT temps FROM lettre WHERE graphAdd = ?", ("no",))

#c.execute("DELETE FROM graphAvg")

# Récupération de la valeur directement en utilisant l'ID
#c.execute("SELECT * FROM tempsMachine ORDER BY id DESC LIMIT 1")
#row = c.fetchall()

#c.execute("INSERT INTO lettre (lettre, tempsTotal, orderID) VALUES (?, ?, ?)", ('A', 60, 'Order123'))

#c.execute("SELECT * FROM lettre ORDER BY id DESC LIMIT 1")
#c.execute("SELECT * FROM operation ORDER BY id DESC LIMIT 2")
#c.execute("SELECT lettre FROM lettre")
#c.execute("SELECT temps FROM lettre ORDER BY id DESC LIMIT 1")
#c.execute("SELECT ordreID FROM ordrePlanifier ORDER BY ordreID DESC LIMIT 1")
#c.execute("SELECT * FROM lettreTemps ORDER BY lettre_id DESC LIMIT 1")


# Afficher la dernière ligne dans la console
#print(row)


# Valider les modifications et fermer la connexion
conn.commit()
conn.close()