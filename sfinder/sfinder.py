#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Carsten Niehaus. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import csv

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_maindlg import Ui_MainDlg 
from studentclasses import *

class MainDialog(QDialog, Ui_MainDlg):

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        #die aktuell vom Benutzer ausgewählte Klasse
        self.aktuelleKlasse = None
        
        #diese Liste enthält alle Klassen der Schule
        self.klassen = [] 
        
        #Pro Schüler gibt es ein Objekt, diese sind in dieser Liste gespeichert
        self.schueler = [] 
        
        #Füge in die QComboBox "Alle" ein für den Fall, dass nichts ausgewählt wurde
        self.klassen.append( "Alle" )
        
        #Lade aus der Datei alle Schüler
        self.loadStudents()
        
        #Erzeuge die Oberfläche
        self.createUi()

        # mit "connect" verbindet man Methoden einer Klasse mit den Signalen 
        # eines Objekts. Das ist nicht pythonspezifisch, sondern commit durch Qt.
        self.connect(self.klassenCombo, SIGNAL("activated(QString)"), self.neueKlasse )
        self.connect(self.such_knopf, SIGNAL("clicked()"), self.suchen )
        self.connect(self.verdeckenCheckBox, SIGNAL("clicked()"), self.updateUi )

    def suchen(self):
        '''Sucht den im Suchfeld gesuchten Schüler'''
        name = self.name_le.text()
        fundliste = []
        for s in self.schuelerListeErstellen():
            if s.hatDatensatz(name):
                print s.name()
                fundliste.append(s)
        
        # Da nun die passenden Schüler gefunden wurden muss mit
        # dieser Liste die Tabelle neu aufgebaut werden.
        self.updateUi(fundliste)
                
    def createUi(self):
        '''Für jede Klasse wird ein String an die QComboBox angefügt.'''
        for k in self.klassen:
            self.klassenCombo.addItem( k )

    def neueKlasse(self, klasse):
       ''' Wenn eine Klasse neu ausgewählt wurde wird die interne
       Variable neu belegt und die Oberfläche neu aufgebaut.'''
       if self.klassenCombo.currentIndex() == 0:
               self.aktuelleKlasse = None
       else:
               self.aktuelleKlasse = klasse
       self.updateUi()

    def schuelerListeErstellen(self):
        ''' Diese Methode stelle die zur Zeit passende Liste an Schülern zusammen.
        Wenn 'Alle' ausgewählt sind, so gibt sie sofort die gesamte Schülerschaft
        zurück, ansonsten geht sie durch die Schüler durch und stellt eine Liste 
        zusammen, die sie schließlich zurückgibt (return)'''
        
        if self.aktuelleKlasse == None:
            return self.schueler

        liste = [] 

        for s in self.schueler:
                k = s.data["klasse"]
                if k == self.aktuelleKlasse:
                        liste.append(s)

        return liste

    def updateUi(self, schuelerListe = None):
        '''Diese Methode baut die Oberfläche neu auf.'''
        
        # Ich finde keine schlauere Methode, um alle Zellen eines QTableWidgets zu löschen
        # Daher muss ich die Tabelle zeilenweise löschen
        while self.tabelle.rowCount() > 0:
                self.tabelle.removeRow(0)

        # Ein einfacher Zähler
        counter = 0

        # Nun muss entschieden werden, welche Liste benutzt wird:
        # Wurde eine Liste an diese Methode übergeben, so soll die
        # benutzt werden, ansonsten muss die Methode schuelerListeErstellen()
        # aufgerufen werden
        liste = []
        if schuelerListe:
            liste = schuelerListe
        else:
            liste = self.schuelerListeErstellen()
            
        for s in liste:
                # Da die Tabelle keine Zeilen hat muss ich pro Schüler eine neue Zeile erzeugen
                self.tabelle.insertRow(counter)
                #print s.debugInfo()
                item_kl = QTableWidgetItem( s.data["klasse"] )
                item_vn = QTableWidgetItem( s.data["vorname"] )
                item_nn = QTableWidgetItem( s.data["nachname"] )
                item_un = QTableWidgetItem( s.data[ "nutzername" ] )
                item_pw = QTableWidgetItem( s.data[ "passwort" ] )

                # Nun bekommt jede Zelle einen passenden Tooltip verpasst
                item_nn.setToolTip( s.toolTipString() )
                item_kl.setToolTip( s.toolTipString() )
                item_vn.setToolTip( s.toolTipString() )
                item_un.setToolTip( s.toolTipString() )
                item_pw.setToolTip( s.toolTipString() )

                self.tabelle.setItem( counter, 0 , item_kl )
                self.tabelle.setItem( counter, 1 , item_vn )
                self.tabelle.setItem( counter, 2 , item_nn )
                if not self.verdeckenCheckBox.isChecked():
                        self.tabelle.setItem( counter, 3 , item_un )
                        self.tabelle.setItem( counter, 4 , item_pw )
                else:
                        self.tabelle.setItem( counter, 3, QTableWidgetItem( "verdeckt" ) )
                        self.tabelle.setItem( counter, 4, QTableWidgetItem( "verdeckt" ) )

                counter += 1

    def loadStudents(self):
        '''In dieser Methode werden die Schuelerdaten geladen'''

        error = None
        fh = None

        try:
                filename = "daten.csv"
                fh = QFile( filename )
                lino = 0
                if not fh.open(QIODevice.ReadOnly):
                        raise IOError, unicode(fh.errorString())
                stream = QTextStream(fh)

                while not stream.atEnd():
                    line = stream.readLine()
                    lino += 1
                    content = line.split(";")
                    nutzername = content[0]
                    passwort = content[1]
                    uid = content[2]
                    vorname = content[3]
                    nachname = content[4]
                    klasse = content[5]

                    if klasse not in self.klassen:
                        self.klassen.append( klasse )

                    s = Schueler()
                    s.setData( nachname, vorname, klasse, nutzername, passwort, uid )
                    self.schueler.append( s )

        except (IOError, OSError, ValueError), e:
                error = "Failed to load: %s on line %d" % (e, lino)

# =========================== Nun wird das Programm ausgeführt ==================== 
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MainDialog()
    form.show()
    app.exec_()

