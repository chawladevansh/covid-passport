import face_recognition
import argparse
import pickle
import cv2
import socket
import pymongo
import time

host = ''
port = 5000
size = 128000

db  =  pymongo.MongoClient().covid_passport

def updateDatabase(db, f_name, l_name, email, dob, vaccine, dose1, dose2, pin):
    stats = {
        "FirstName": f_name,
        "LastName": l_name,
        "Email": email,
        "DateOfBirth": dob,
        "VaccineName": vaccine,
        "Dose1Date": dose1,
        "Dose2Date": dose2,
        "PIN": pin,
        "MsgID": "16$" + str(time.time()),
    }
    db.utilization.insert_one(stats)

def insertToDB(f_name, l_name, email, dob, vaccine, dose1, dose2, pin):
    global db
    updateDatabase(db, f_name, l_name, email, dob, vaccine, dose1, dose2, pin)
    print('Record Created')

def getFromFB(f_name, l_name, pin):
    global db
    utilization = db["utilization"]
    for x in utilization.find({"FirstName": f_name, "LastName":l_name, "PIN":pin}, {"MsgID":0}):
        print(x)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
print('Client-Server connected')

client, address = s.accept()

while True:
    data =client.recv(size)
    data_unpickled = pickle.loads(data)

    if(data_unpickled["data"][0] == 0):
        getFromFB(data_unpickled["data"][1], data_unpickled["data"][2], data_unpickled["data"][3])
        print('Get from DB')
    elif(data_unpickled["data"][0] == 1):
        insertToDB(data_unpickled["data"][1], data_unpickled["data"][2], 
                   data_unpickled["data"][3], data_unpickled["data"][4], 
                   data_unpickled["data"][5], data_unpickled["data"][6], 
                   data_unpickled["data"][7], data_unpickled["data"][8])
        print('Add to DB')

client.close()