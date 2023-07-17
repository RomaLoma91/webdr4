import mimetypes
import urllib.parse
from datetime import datetime
import json

route = urllib.parse.urlparse('http://localhost:3000')
# print(route.netlock)
mime_type, *mt = mimetypes.guess_type('filename.mp3')
# print(mt)
# print(datetime.now())
data = 'username=RomaLoma91&Lets+play%21'
data = urllib.parse.unquote_plus(data)
current_time = str(datetime.now())
data_dict = {key: value for key, value in [el.split('=') for el in data.split('&')]}
data = {current_time: data_dict}

with open('storage.json', 'r') as fd:
    data = json.load(fd)
print (data)