import os
import cv2
import pickle
import re
import time
import glob
import socket
import face_recognition
from flask import Flask
from flask import Response, flash
from flask import render_template
from sys import getsizeof
from flask import request
from flask import redirect
from flask_wtf import FlaskForm
from imutils import paths
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SECRET_KEY']='DevanshAndJayTeam16'
camera = cv2.VideoCapture(0)

host = ''
port = 5000
size = 128000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
print('[Client 01] - Connecting to ', host, ' on port', port, end='\n\n')

dataset_path = '/home/devansh/covid-passport/Dataset'
model_path = '/home/devansh/covid-passport/model.pickle'

def resize_image(image):
    dim = (int(image.shape[1]/3), int(image.shape[0]/3))
    resized = cv2.resize(image, dim)
    return resized

class get_user_data(FlaskForm):
    f_name = StringField(label=('First Name'))
    l_name = StringField('Last Name')
    email = StringField('Email')
    dob = StringField('Birthday')
    vaccine = StringField('Vaccine')
    dose1 = StringField('Dose 1')
    dose2 = StringField('Dose 2')
    pin = StringField('6 Digit Pin')
    submit = SubmitField('Submit')

class get_user_pass(FlaskForm):
    pin = StringField('Pin')
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    global camera
    return Response(get_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')  

def get_video(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    form = get_user_data()

    # TODO : get user pin

    if form.validate_on_submit():
        flag = 1
        data_payload = (flag,
                        form.f_name.data,
                        form.l_name.data,
                        form.email.data,
                        form.dob.data,
                        form.vaccine.data,
                        form.dose1.data,
                        form.dose2.data,
                        form.pin.data)

        global camera
        for i in range(15):
            ret, frame = camera.read()
            frame = resize_image(frame)
            cv2.imwrite(os.path.join(dataset_path , form.f_name.data + '-' + form.l_name.data + '-' + str(i) + '.jpg'), frame)
            time.sleep(0.2)

        # Encode Faces
        imagePaths = list(paths.list_images(dataset_path))
        knownEncodings = []
        knownNames = []

        for imagePath in imagePaths:
            print(imagePath)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb,model='cnn')
            print('Encoding ...')
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                knownEncodings.append(encoding)
                name = os.path.basename(imagePath).split('-')
                knownNames.append(name[0] + ' ' + name[1])

        data = {"encodings": knownEncodings, "names": knownNames, "data" : data_payload}

        data_pickled = pickle.dumps(data)
        s.send(data_pickled)
        print('Data Sent to Server')
        f = open('model.pickle', "wb")
        f.write(data_pickled)
        f.close() 

        return render_template('captured.html')
    return render_template('generate.html', form=form)

@app.route('/get_passport', methods=['GET', 'POST'])
def get_passport():
    form = get_user_pass()
    data = pickle.loads(open(model_path, "rb").read())

    if form.validate_on_submit():
        global camera
        ret, frame = camera.read()
        frame = resize_image(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
        
        name = name.split()
        data_payload = (0, name[0], name[1], form.pin.data)

        data_dict = {"data":data_payload}
        data_pickled = pickle.dumps(data_dict)
        s.send(data_pickled)
        print('Data Sent to Server')

        u_data = s.recv(size)
        user_data = pickle.loads(u_data)
        print(user_data)

        user_details = {
        'f_name': user_data[0],
        'l_name': user_data[1],
        'email' : user_data[2],
        'dob' : user_data[3],
        'vaccine' : user_data[4],
        'dose1' : user_data[5],
        'dose2' : user_data[6]}

        return render_template('display_passport.html', data=user_details)

    return render_template('get_images.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True)