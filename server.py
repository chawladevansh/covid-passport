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

# db  =  pymongo.MongoClient().TEST
# updateDatabase(db, f_name, l_name, email, dob, vaccine, dose1, dose2, pin)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
print('Client-Server connected')

client, address = s.accept()

while True:
    data =client.recv(size)
    data_unpickled = pickle.loads(data)

    if(data_unpickled["data"][0] == 0):
        print('Get from DB')
    elif(data_unpickled["data"][0] == 1):
        print('Add to DB')

client.close()