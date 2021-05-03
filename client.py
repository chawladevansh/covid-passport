''' TODO 

 - Facial recognition
 - Flask video streaming

'''
import os
import cv2
import time
import pickle
import argparse
import face_recognition
from imutils import paths
from imutils.video import VideoStream
from flask import Response, flash
from flask import Flask
from flask import render_template
from flask import request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

app = Flask(__name__)
camera = cv2.VideoCapture(0)

dataset_path = '/home/devansh/covid-passport/Dataset'
model_path = '/home/devansh/covid-passport/Models/model.pickle'

def resize_image(image):
    dim = (int(image.shape[1]/3), int(image.shape[0]/3))
    resized = cv2.resize(image, dim)
    return resized

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

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


@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    global camera
    return Response(get_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_images', methods=["GET","POST"])
def process_images():
    global camera
    for i in range(15):
        ret, frame = camera.read()
        frame = resize_image(frame)
        cv2.imwrite(os.path.join(dataset_path , "image" + str(i) + '.jpg'), frame)
        time.sleep(0.5)
    return ('')

@app.route('/new_user', methods=["GET","POST"])
def new_user():
    if request.method == 'POST':
        print(request.form.get('name'))
        print(request.form.get('dob'))
        print(request.form.get('vaccine'))
        print(request.form.get('dose1'))
        print(request.form.get('dose2'))
    return render_template('new_user_form.html')

# ''' @param

#     - Dataset directory
#     - serialized facial embeddings path
#     - face detection model to use
# '''

# # Encode Faces
# imagePaths = list(paths.list_images(dataset_path))
# knownEncodings = []
# knownNames = []

# for imagePath in imagePaths:
#     print(imagePath)
#     image = cv2.imread(imagePath)
#     rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     boxes = face_recognition.face_locations(rgb,model='cnn')
#     print('Encoding ...')
#     encodings = face_recognition.face_encodings(rgb, boxes)

#     for encoding in encodings:
#         knownEncodings.append(encoding)
#         knownNames.append(user)

# # pickle dump the facial encodings and names to disk
# data = {"encodings": knownEncodings, "names": knownNames}
# f = open(model_path, "wb")
# f.write(pickle.dumps(data))
# f.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True)