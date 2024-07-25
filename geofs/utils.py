"""

MIT License

Copyright (c) 2024 rico-949

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


"""



import json
import importlib.resources
from .models import Aircraft, Player
from .endpoints import *
import requests

def get_aircraft(id):
        with importlib.resources.open_text('geofs.py', 'data/aircraftcodes.json') as file:
            codes = json.load(file)
        if id in codes:
            data = {"id": {id}, "name": data[id]["name"]}
            return Aircraft(data)
        else:
            return {"id": {id}, "name": "Unknown"}


def get_player(acid):
     body = {
          "id":"",
          "gid": None
     }
     response = requests.post(map_endpoint, body)
     response_body = json.loads(response.text)
     users = response_body["users"]
     for user in users:
        if user.get('acid') == acid:
            return Player(user)
        return None
