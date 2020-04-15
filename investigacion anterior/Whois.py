# Muestra información del Sitio - www.properati.com

import whois
import sys
from time import sleep
from time import ctime
import time


def getwhois(url):
    try:
        print("Buscando información del sitio...")
        data = whois.whois(url)
        print("Consulta éxito!")
        print(data)
        return data
    except:
        print("Consulta Error!")
        pass

getwhois("https://www.properati.com")
