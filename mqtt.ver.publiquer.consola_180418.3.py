
#!/usr/bin/env python 1
# -*- coding: utf-8 -*-

#Libreria para el MQTT
import paho.mqtt.client as mqtt

import sys
import shutil
import time

#Libreria capturar IP (NECESARIA INSTALAR)
try:           #Python 3.x
    from urllib.request import urlopen
except:        #Python 2.x
    import urllib         


proyect = "mqtt.ver.publiquer.consola"
version = "V180418.3"
client_name ="NOMBRE_CLIENTE"
filename_log ="MQTT.LOG"
urlIP = 'https://martianoids.com/myip.txt' #Web donde realizaremos el scrapping a nuestra direccion IP
Connected = False           #Flag que indica que se esta conectado al servidor
msgserver = ""
seg = 10
updateFlag=False            #Flag que solicita que se reenvie la informacion de la IP del PC

globalUpdate = "UpdateIP"; 

#DATOS DE CONEXION CON EL SERVIDOR
broker_address= "m23.cloudmqtt.com"
port = 0
user = "user"
password = "pass"

#***************TITULO*********************
print("--------------------")
print("****MQTT CONSOLA****")
print("--------------------")
#***************FUNCIONES******************

def on_connect(client, userdata, flags, rc):

    global Connected                #Use global variable
    if (rc==0 and Connected==False):
        client.connect_flag=True        #Flag de conexion.
        Connected = True                #Signal connection
        print("Se establecion conexion y autentificacion con el servidor : "+ broker_address)
        writeinfile(filename_log,"Conectado")
    elif (rc!=0):
        print("Error de conexion - Codigo de resultado: "+ str(rc))
        if (rc == 5) :
            print("Posible fallo de autentificacion con el servidor"+ str(rc))
    else:
        print("Codigo de resultado: "+ str(rc))

    client.subscribe("#")
    print ("--------------------------")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    print(time.strftime("%d/%m/%y - %H:%M ->") + msg.topic+" "+str(msg.payload))

    if (msg.topic == "Update" and (str(msg.payload) == globalUpdate or str(msg.payload) == user)):
        print ("Solicitan update datos")
        global updateFlag
        client.publish("IPPublica", getipextern())
    else :
        global msgserver
        msgserver = ""
        msgserver = msg.topic +" "+ str(msg.payload)
        writeinfile(filename_log, msgserver)
        print ("--------------------------")


def on_publish(client,userdata,result):             #create function for callback
    print("\nSe publica el mensaje\n")

def on_log(mqttc, obj, level, string):
    print(string)
############################################################################
#Escribir fichero LOG
############################################################################
def writeinfile (ficherotxt,text):                              #Funcion de log
    print("El mensaje "+text+" se registra en el fichero " + ficherotxt+".txt")
    f = open (ficherotxt+'.txt','a')
    f.write(time.strftime('%d %b %y - %H:%M -> '))
    f.write(text+'\n')
    f.close()

############################################################################
# Esta funcion coge la IP publica para ser publicada
def getipextern():
    try:
        try:     #Python 3.x
            ip = urlopen(urlIP).read() # esta URL puede ser reemplazada con otra que preste similar servicio
        except:   #Python 2.x
            ip = urllib.urlopen(urlIP).read() # esta URL puede ser reemplazada con otra que preste similar servicio
    except IOError:
        ip = "No Conexion"
    print ("La IP publica es : " + str(ip.decode("utf-8")))
    return ip.decode()


############################################################################
#PROGRAMA ()
############################################################################

def loop_program():


    client.loop_start()

    client.publish("IP Publica", getipextern()) # Publicamos IP publica PC
    print ("--------------------------")

    while (1):

        if (time.time()%60 == 0):
            client.publish("IP Publica", getipextern()) # Publicamos IP publica PC
            time.sleep (1)

############################################################################
# CONFIGURACION DEL PROGRAMA
############################################################################

#Configuracion de los servicios MQTT
client = mqtt.Client(client_name)
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
#client.on_log = on_log  # Uncomment to enable debug messages

#Realizamo la conexion si esta no es satisfactoria se cierra el programa
try:
    client.connect(broker_address, port=port, keepalive=60)
except:
    print("No se pudo conectar con el MQTT Broker...")
    print("Cerrando...")
    sys.exit()

    
#Bucle del programa hasta que se elije salir por interrupcion por teclado
try:
    loop_program ()        #Aqui se ejecuta el cuerpo del verdadero programa
except KeyboardInterrupt:  #Precionar Crtl + C para salir
    print("Cerrando...")
    client.disconnect()    #Desconectamos del servidor
    client.loop_stop()     #Paramos el proceso mqtt 

exit = raw_input("PROGRAMA FINALIZADO") #***FIN***