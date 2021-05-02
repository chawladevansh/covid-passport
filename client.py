''' TODO 

 - Facial recognition
 - Flask video streaming

'''
import os
import cv2
import pickle
import argparse
import face_recognition
from imutils import paths
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template

app = Flask(__name__)

def get_video():
    camera = cv2.VideoCapture(0)  
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(get_video(), mimetype='multipart/x-mixed-replace; boundary=frame')


# def resize_image(image):
#     dim = (int(image.shape[1]/3), int(image.shape[0]/3))
#     resized = cv2.resize(image, dim)
#     return resized

# dataset_path = '/home/devansh/covid-passport/Dataset'
# model_path = '/home/devansh/covid-passport/Models/model.pickle'
# user = input('Enter Name : ')

# cap = cv2.VideoCapture(0)

# # Capture 10 images for training dataset
# for i in range(3):
#     ret, frame = cap.read()
#     frame = resize_image(frame)
#     cv2.imwrite(os.path.join(dataset_path , user + str(i) + '.jpg'), frame)

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
    app.run(debug=True)