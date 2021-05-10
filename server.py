import face_recognition
import argparse
import pickle
import cv2
import socket
import pymongo
import time

# Define host port and buffer size
host = ''
port = 5000
size = 128000

# Instantiate MongoDB instance
db  =  pymongo.MongoClient().covid_passport

# Function to update the database
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

# Insert user data into database
def insertToDB(f_name, l_name, email, dob, vaccine, dose1, dose2, pin):
    global db
    updateDatabase(db, f_name, l_name, email, dob, vaccine, dose1, dose2, pin)
    print('Record Created')

# get user data from database
def getFromFB(f_name, l_name, pin):
    global db
    utilization = db["utilization"]
    for x in utilization.find({"FirstName": f_name, "LastName":l_name, "PIN":pin}, {"MsgID":0}):
        return x

# Socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
print('Client-Server connected')

client, address = s.accept()

while True:
    data = client.recv(size)
    data_unpickled = pickle.loads(data)

    # Send user data to client
    if(data_unpickled["data"][0] == 0):
        x = getFromFB(data_unpickled["data"][1], data_unpickled["data"][2], data_unpickled["data"][3])
        
        user_data = (str(x['FirstName']), str(x['LastName']), 
                     str(x['Email']), str(x['DateOfBirth']),
                     str(x['VaccineName']), str(x['Dose1Date']),
                     str(x['Dose2Date']))

        data_pickle = pickle.dumps(user_data)

        if(data):
            client.send(data_pickle)
            print('Data sent to client')

    # Recieve user data from client
    elif(data_unpickled["data"][0] == 1):
        insertToDB(data_unpickled["data"][1], data_unpickled["data"][2], 
                   data_unpickled["data"][3], data_unpickled["data"][4], 
                   data_unpickled["data"][5], data_unpickled["data"][6], 
                   data_unpickled["data"][7], data_unpickled["data"][8])
        print('Add to DB')

# close client connection
client.close()