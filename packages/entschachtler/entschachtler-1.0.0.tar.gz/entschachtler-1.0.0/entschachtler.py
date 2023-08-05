"""entschachtler.py ist ein Modul, dass eine Funktion namens print_lvl() bereitstellt,
die eine Liste mit beliebig vielen eingebetteten Listen ausgibt"""

def print_lvl(liste):
    """Diese Funktion erwartet ein positionelles Argument namens "liste",
    das eine beliebige Python-Liste ist.Jedes Element der liste wird auf dem Bildschirm
    jeweils in einer eigenen Zeile ausgegeben"""
    for element in liste:
        if isinstance(element, list):
            print_lvl(element)
        else:
            print(element)

            
