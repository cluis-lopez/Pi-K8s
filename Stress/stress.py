import json
import requests
import random
import sys
import time

BASE_URL='http://192.168.1.111:8080'
MAXINSERTS=10

def getRandomCustomer():
    req = requests.get(BASE_URL + '/cliente')
    if (req.status_code == 200 and req.headers['Content-Type'] == 'application/json'):
        customer = json.loads(req.text)
        return customer
    else:
        raise Exception("Error retrieving page /cliente")
         
def getOrders(custId):
    req = requests.get(BASE_URL + '/pedidosCliente?custid=' + str(custId))
    if (req.status_code == 200 and req.headers['Content-Type'] == 'application/json'):
        orders = json.loads(req.text)
        return orders
    else:
        raise Exception("Error retrieving page /pedidosClient")
        
def regenerateOrders(custId, remove, insert):
    params = "custid=" + str(custId) + "&remove=" + str(remove) + "&insert=" + str(insert)
    req = requests.get(BASE_URL + '/pedidosRandom?' + params)
    if (req.status_code == 200 and req.headers['Content-Type'] == 'application/json'):
        orders = json.loads(req.text)
        return orders
    else:
        raise Exception("Error retrieving page /pedidosRandom")
    
def singleTransaction():
    message=""
    try:
        starttime=time.time()
        customer = getRandomCustomer()
        currentOrders = getOrders(customer['id'])
        if (len(currentOrders)>0):
            remove = random.randrange(len(currentOrders))
        else:
            remove = 0
        insert = random.randrange(MAXINSERTS)
        newOrders = regenerateOrders(customer['id'], remove, insert)
        message = "Cliente " + customer['nombre'] + " " + customer['apellido']
        message = message + ", tenia " + str(len(currentOrders)) + " pedidos"
        message = message + ". Se han borrado " + str(remove) +" e insertado " + str(insert) +" pedidos"
        message = message + ". Nuevos pedidos: " + str(len(newOrders))
        message = message + "\nElapsed Time: " + "{:.2f}".format(time.time()-starttime) + " sg"
    except Exception as err:
        message = "Se ha producido un error: " + str(err)

    return message

def usage():
    print("Usage stress delay_value")

if (__name__ == '__main__'):
    if (len(sys.argv) < 2):
        print(singleTransaction())
        exit()
    else:
        try:
            delay = int(sys.arv[1])
        except ValueError as err:
            print(err)
            usage()
            exit()


