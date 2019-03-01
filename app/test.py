import requests
import json


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
 
data = open('img.jpg', 'rb')
x = requests.post(face_api_url , params=params, headers=headers, data=data)
print(json.loads(x.text))