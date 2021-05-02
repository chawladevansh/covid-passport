import face_recognition
import argparse
import pickle
import cv2

model_path = '/home/devansh/covid-passport/Models/model.pickle'
data = pickle.loads(open(model_path, "rb").read())

cap = cv2.VideoCapture(0)
ret, image = cap.read()
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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

for ((top, right, bottom, left), name) in zip(boxes, names):
	# draw the predicted face name on the image
	cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
	y = top - 15 if top - 15 > 15 else top + 15
	cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
		0.75, (0, 255, 0), 2)

# show the output image
cv2.imshow("Image", image)
cv2.waitKey(0)