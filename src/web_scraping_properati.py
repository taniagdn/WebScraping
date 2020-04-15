'''
PRACTICA Nro. 1: WEB SCRAPING DEL PORTAL INMOBILIARIO PROPERATI
Python 3.7
___________________________________________________________________________________________________
UOC - MASTER UNIVERSITARIO EN CIENCIA DE DATOS - ABRIL 2019
TIPOLOGÍA Y CICLO DE VIDA DE LOS DATOS

AUTORES: Tania Gualli Culqui y Fernando Meza Ibarra

DESCRIPCIÓN DE LA PRÁCTICA: Aplicación de las técnicas de Web Scraping en el portal inmobiliario 
Properati, el cual promociona la venta de bienes inmuebles en Ecuador.
Se ha considerado obtener un dataset de todas las ofertas de bienes muebles inmuebles ofertados
para la ciudad de Quito, el cual considera información de departamentos, casas, terrenos / lotes.

Se obtiene DATASET con los siguientes campos:
 * descripcion_conjunto
 * tipo
 * precio
 * localizacion
 * fecha_publicacion
 * area
 * num_habitaciones
 * proy

___________________________________________________________________________________________________
'''

# llamada a librerias
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
from urllib.error import HTTPError
from datetime import datetime, date, time, timedelta
import calendar
import time

# Condiciona el acceso del Agente al Sitio de Properati
import requests
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
response = session.get('https://www.properati.com.ec/robots.txt')

if response == 200 : # devuelve Éxito= 200
    # Generamos archivo robots.txt
    robotsTXT = open("robots.txt","w")
    try:
        html = urlopen('https://www.properati.com.ec/robots.txt')
    except HTTPError as err:
           print(err)
    except URLError:
        print('Error de acceso..Web puede haber sido bloqueada')
    else:
        robots = BeautifulSoup(html.read(),'lxml')
        robotsTXT.write(str(robots))    
    robotsTXT.close()
   # Finaliza generación de archivo y cierra escritura
# Fin de control acceso User-Agent al sitio


'''MECANICA:
   El portal presenta páginas con 20 ítems cada una. 
   El número de páginas fluctúa dependiendo del filtro utilizado.
   El ejemplo filtra TODOS los bienes inmuebles que están a la venta en la ciudad de Quito.
   Existen 50 páginas de ítems que se pueden acceder.
'''
# CREA ARCHIVO
# Se prepara el dataset con los campos requeridos
# Dataset tendrá formato CSV (valores separados con ";")
nombre_dataset = "valoraciondeinmueblesquito.csv"

# Abrimos archivo para escritura
file = open(nombre_dataset,"w")

# GRABA ENCABEZADOS
# Titulos del Dataset - Se usa un separador distinto a la coma, puesto que en la estructura HTML
# se usa a la coma "," como separador de valores. Por tal razón usaremos al ";" en el Dataset
encabezado = "NOMBRE_CONJUNTO;TIPO_BIEN;PRECIO;LOCALIZACIÓN;FECHA_PUBLICACIÓN;ÁREA m²;NUM_HABITACIONES;NOMBRE_PROYECTO\n"
file.write(encabezado)
# Fin de grabación de encabezado

# INICIA BARRIDO 

# Se usa bandera para cada página que se recorre.
# Cada página muestra 20 items
Num_Pagina = 1

# INICIA WHILE
# Total páginas 50  (Dataset flutuará entre los 1000 ítems)
# El procesa de datos implica limpiar algunos caracteres innecesarios como:
# (punto decimal, metros cuadrados, símbolo de moneda, etc)
while Num_Pagina <= 50:
    try:
        if Num_Pagina == 1:
            html = urlopen('https://www.properati.com.ec/quito/venta/') # Página Inicial
        else:    
            html = urlopen('https://www.properati.com.ec/quito/venta/'+str(Num_Pagina)+'/') #paginas desde la 2 a la 50
    except HTTPError as err:
        print(err)
    except URLError:
        print('Error de acceso..Web puede haber sido bloqueada')
    else:
        # Se crea objeto soup de BeautifulSoup para parsear y se utiliza lxml que es un parser rápido
        soup = BeautifulSoup(html.read(),'lxml')
        
        # Accedemos con el objeto tag a la etiqueta del artículo con la clase "item"
        tags = soup.findAll("article",{"class":"item"})

# Recorremos de 1 a 20 ítems por página
        for tag in tags:
            
            # Proyecto
            inmuebleProy = tag.findAll("p",{"class":"ribbon"})
            if len(inmuebleProy) > 0:
                Tag_Proy = inmuebleProy[0].find('span')
                if Tag_Proy != None:
                    proy = Tag_Proy.text.strip()                    
                else:
                    proy = '' # Sino, guarda blanco
            else:
                proy = ''     # Sino guarda blanco  
                    
            # Se obtiene la descripcion del anuncio
            inmuebleDescripcion = tag.findAll("a",{"class":"item-url"})
            descripcion_conjunto = inmuebleDescripcion[0].text.strip()   
            
           # Se obtiene el tipo de inmueble
            inmuebleTipo = tag.findAll("p",{"class":"property-type"})
            tipo = inmuebleTipo[0].text.strip()              

            # Se obtiene el precio del inmueble
            inmueblePrecio = tag.findAll("p",{"class":"price"})
            precio = inmueblePrecio[0].text.strip()
            precio = precio.replace ( ".", "")  # se quita punto decimal de la cadena
            
            # Se elimina simbolo de moneda "$", que esta al inicio
            precio = precio[1:len(precio)]

            # Sector donde se encuentra el bien inmueble
            inmuebleLocalizacion = tag.findAll("p",{"class":"location"})
            localizacion = inmuebleLocalizacion[0].text.strip()            

            # Fecha del anuncio
            # Obtiene todos los anuncios- desde 2019 hasta los publicados en el mes de abril 2020
            inmuebleFecha = tag.findAll("p",{"class":"date-added"})
            fecha = inmuebleFecha[0].text.strip() 
            if fecha == "Publicado hoy":
                fecha1 = date.today()
                fecha = fecha1.strftime('%d/%m/%Y')                
            else:
                dia = fecha[0:2]
                mes = fecha[6:len(fecha)]
                #Chequea si la publicación fue hecha en 2019 o en los 4 primeros meses de 2020
                if mes == "enero" or mes == "febrero" or mes == "marzo" or mes == "abril":
                    anio= "2020" 
                else:
                    anio = "2019"
                fecha = dia+"/"+mes+"/"+anio
            
            fecha_publicacion = fecha
            #datetime.strptime(fecha, formato2)  
           
            # Area en m² del inmueble
            # Importante: Algunos ítems no registran valor de área
            inmuebleHabitaciones = tag.findAll("p",{"class":"rooms"})
            if len(inmuebleHabitaciones) > 0:
                Tag_Area = inmuebleHabitaciones[0].find('span')
                if Tag_Area != None:
                    area = Tag_Area.text.strip()                    
                    area = area[:len(area)-2]  # Se elimina texto al final (m²)
                else:
                    area = '' # Sino, guarda blanco
            else:
                area = ''     # Sino guarda blanco        

            # Muestra el número de habitaciones del bien inmueble
            # Algunos ítems no registran este dato
            if len(inmuebleHabitaciones) > 0:
                err_tag = inmuebleHabitaciones[0].find('span')
                if err_tag != None:
                    err_tag.extract()
                    num_habitaciones = inmuebleHabitaciones[0].text.strip()
                    num_habitaciones = num_habitaciones[0:1]  # Se elimina la palabra "habitaciones"
                else:
                    num_habitaciones = inmuebleHabitaciones[0].text.strip()
                    num_habitaciones = num_habitaciones[0:1] # Se elimina la palabra "habitaciones"
            else:  num_habitaciones = '' # Sino, guarda blanco           

            # Guarda datos del dataset en formato CSV
            file.write(descripcion_conjunto+";"+tipo+";"+precio+";"+localizacion+";"+fecha_publicacion+";"+area+";"+num_habitaciones+";"+proy+"\n")

    Num_Pagina += 1
    time.sleep(30)

#Cierra archivo Dataset despúes de escritura
file.close()

# FIN DE PROCESO WEB SCRAPING
