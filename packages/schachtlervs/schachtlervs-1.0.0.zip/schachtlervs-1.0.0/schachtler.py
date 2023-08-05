"""Das Modul beinhaltet eine rekursive Funktion print_lvl die
    eine Liste mit bleiebig vielen eingebetteten Listen ausgiebt"""

def print_lvl(liste):
        """ Die Funktion print_lvl durchläuft die übergeben eine übergebene List 
            und prüft ob das aktuelle Element eine eingebttete Liste ist, falls ja wird dei Funktion
            mit dem Element nochmals ausgerufen und falls es keine Liste ist der Inhalt auf einer neuen Zeile ausgegeben"""

        for element in liste:
                if isinstance(element, list):
                        print_lvl(element)
                else:
                        print(element)
