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
    elapsedTime=0.0
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
        elapsedTime=time.time()-starttime
        message = "Cliente " + customer['nombre'] + " " + customer['apellido']
        message = message + ", tenia " + str(len(currentOrders)) + " pedidos"
        message = message + ". Se han borrado " + str(remove) +" e insertado " + str(insert) +" pedidos"
        message = message + ". Nuevos pedidos: " + str(len(newOrders))
        message = message + "\nElapsed Time: " + "{:.2f}".format(elapsedTime) + " sg"
    except Exception as err:
        message = "Se ha producido un error: " + str(err)

    return (message, elapsedTime)

def mainLoop(delay):
    count = parcialCount = 0
    average = 0.0
    while True:
        d = delay+(random.uniform(-delay/2,delay/2))
        time.sleep(d)
        ret = singleTransaction()
        count += 1
        parcialCount += 1
        average=average+ret[1]/parcialCount
        if (count % 5 == 0):
            print("Realizadas " + str(count) + " transacciones. Tiempo medio para cada transaccion: " + "{:.2f}".format(average))
            parcialCount = 0
            average = 0.0

def usage():
    print("Usage stress delay_value")

if (__name__ == '__main__'):
    if (len(sys.argv) < 2):
        ret = singleTransaction()
        print(ret[0])
        exit()
    else:
        try:
            delay = float(sys.argv[1])
        except ValueError as err:
            print(err)
            usage()
            exit()
        mainLoop(delay)

