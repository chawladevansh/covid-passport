import face_recognition
import argparse
import pickle
import cv2
import socket

host = ''
port = 5000
size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
print('Client-Server connected')

client, address = s.accept()
while 1:
    data_pickled = client.recv(size)
    data = pickle.loads(bytes_object)
# data = pickle.loads(open(model_path, "rb").read())

    cap = cv2.VideoCapture(0)
    ret, image = cap.read()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cap.release()
    print('Image captured')
    print('This might take a while..')
    boxes = face_recognition.face_locations(rgb,model='cnn')
    print('Encoding...')
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"],encoding)
        name = "Unknown"
        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
        names.append(name)

    '''
        unpickle data and add to mongo db
        add encoded image pickle to mongo db
    '''


    # show the output image
    cv2.waitKey(0)