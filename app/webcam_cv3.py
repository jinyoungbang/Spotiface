import cv2
import sys
import logging as log
import datetime as dt
import threading
import time
import requests
import json
import random


face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
        'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
};

headers = {
    'Content-Type': 'application/octet-stream', 
    'Ocp-Apim-Subscription-Key': 'a1396b3f3f4940fb8d9151a0d8e0970f'
}

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)
anterior = 0
starttime=time.time()


#oAuthToken = raw_input("Please Enter a OAuth Token from Spotify: ")
oAuthToken = 'BQDI1m4e06q5Fd545taq-OZt0I-1LrbN1hFGwpTUYpGqOjdfqhFQbqiA6sIaASPjEuG-cfTEapcVurhVYqoddPm_JSVFdSHYUyToPD-wugbIL7j82ljU3-e2gDSZW5bGPvKP7TaS6RuXStDm5krD3N-WaX4rq6rrwkY9mrfpYqV8hGMofHVtje-r1ROlwmekqNvWlGoCM6KpTs6JBUm_tiuLDTLLdCXJ7AUddbGctE9CJG_yfFLTNsLXAA'
#genre = raw_input("Please Enter Your Favorite Genre: ")
genre = 'classical'
#genre = raw_input("Please Enter Your Device ID: ")
device_id = '787e521a58709c09c46b312a08dbb01f7483cddd'

def calculate_valence(emotions):
    neutral_factor = 0.5
    happiness = emotions['happiness']/2
    sadness = emotions['sadness']/-2
    final_factor = neutral_factor + happiness + sadness
    return final_factor

def grab_song(inputtoken, inputgenre, inputvalence):
    spotify_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + inputtoken,
    }
    spotify_params = (
        ('limit', '100'),
        ('market', 'ES'),
        ('seed_genres', inputgenre),
        ('target_valence', inputvalence),
    )
    response = requests.get('https://api.spotify.com/v1/recommendations', headers=spotify_headers, params=spotify_params)
    pretty_json = json.loads(response.text)['tracks'][random.randint(0,101)]
    return pretty_json

def play_song(inputtoken, device_id, track_uri):
    spotify_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + inputtoken,
    }
    spotify_params = (
        ('device_id', device_id),
    )
    data = '{"uris":[' + '"'+track_uri+'"' + '],"position_ms":0}'
    response = requests.put('https://api.spotify.com/v1/me/player/play', headers=spotify_headers, params=spotify_params, data=data)

while True:
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    #this will only run if it detects a face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        print("FACE FOUND")

        img_name = "current_face.png"
        cv2.imwrite(img_name, frame)

        data = open('current_face.png', 'rb')
        json_data = requests.post(face_api_url , params=params, headers=headers, data=data)
        pretty_json = json.loads(json_data.text)
        emotions = pretty_json[0]["faceAttributes"]['emotion']
        valence = calculate_valence(emotions)
        current_song = grab_song(oAuthToken, genre, valence)
        print("Playing ", current_song["name"], " with valence as ", valence)
        play_song(oAuthToken, device_id, current_song["uri"])
        time.sleep(5)

    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))


    cv2.imshow('Video', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.imshow('Video', frame)


# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()


