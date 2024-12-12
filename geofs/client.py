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



import requests
import json
import importlib.resources
from typing import Callable
from threading import Thread
import time
import logging

from .endpoints import *
from .models import *
from .body import *
from . import utils as u

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Client:

    #If desired, the geofsSessionID and geofsAccountID can be passed as blank, but multiplayer related methods will be useless (they are broken anyways)

    def __init__(self, geofsSessionID, geofsAccountID):
        self.sessionID = geofsSessionID
        self.accountID = geofsAccountID
        self.myID = None
        self.lastMsgID = None
        self.chat_body = update_body.copy()
        self.chat_body["sid"] = self.sessionID
        logging.info("Initializing Session ID")
        self.chat_body["acid"] = self.accountID
        logging.info("Initializing Account ID")
        self.chat_body["id"] = None
        self.chat_body["ti"] = None
        logging.info("Standard update packet formed")

        try:
            # Perform handshake to initialize session details
            logging.info("Performing handshake with GeoFS servers")
            response = requests.post(chat_endpoint, json=self.chat_body, cookies={"PHPSESSID": self.sessionID})
            response.raise_for_status()  # Raise an exception for HTTP errors
            hs_response = response.json()  # Parse JSON response

            # Update client state based on server response
            logging.info("Handshake sucsessful")
            self.myID = hs_response.get("myId")
            self.lastMsgID = hs_response.get("lastMsgId")
            self.chat_body["id"] = hs_response.get("myId")
            self.chat_body["ci"] = hs_response.get("lastMsgId")
            self.chat_body["ti"] = hs_response.get("serverTime")
            logging.info("GeoFS Client successfuly initialized")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during initialization: {e}")
            raise RuntimeError("Failed to initialize GeoFS Client. Check your connection or credentials.")
        except KeyError as e:
            logging.critical(f"Unexpected response format during initialization: {e}")
            raise RuntimeError("Server response is missing expected fields.")
        

    #this mf took me way too long to finish
    def get_aircraft(self, id: str):
        id = str(id)
        with importlib.resources.open_text('geofs.data', 'aircraftcodes.json') as aircraft_raw:
            ac_codes = json.load(aircraft_raw)
        if id in ac_codes:
            data = {"id": id, "name": ac_codes[id]}
            return Aircraft(data)
        return Aircraft({"id": id, "name": "Unknown"})

    def get_player(self, acid: str):
        response = json.loads(requests.post(map_endpoint, json = map_body).text)
        users = response["users"]
        for user in users:
            if user.get('acid') == acid:
                return Player(user) 
        return None
            
    def get_playerList(self):
        response = json.loads(requests.post(map_endpoint, json = map_body).text)
        users = [Player(user) for user in response["users"]]
        if users:
            return users
        return None
    
    def get_base(self, icao: str):
        icao = str(icao)
        with importlib.resources.open_text('geofs.data', 'airports.json') as airports_raw:
            airports = json.load(airports_raw)
        for country, country_airports in airports.items():
            if icao in country_airports:
                airport = {
                    "icao": icao,
                    "coord": country_airports[icao],
                    "cc": country
                }
                return Airport(airport)
    
    #HOLY FUCK THIS WAS PAINFUL
    def get_messages(self):
        self.chat_body["ci"] = self.lastMsgID  
        self.chat_body["id"] = self.myID
        raw_response = requests.post(chat_endpoint, json=self.chat_body, cookies={"PHPSESSID": self.sessionID}).text
        if raw_response:
            response = json.loads(raw_response)
            self.myID = response["myId"]
            self.lastMsgID = response["lastMsgId"]
            return [Message(msg) for msg in response["chatMessages"]]
        else:
            return []

    
    def send_message(self, msg: str):
        msg_body = self.chat_body.copy()
        msg_body["m"] = msg
        response = json.loads(requests.post(chat_endpoint, json = msg_body, cookies = {"PHPSESSID": self.sessionID}).text)
        self.myID = response["myId"]
    

    def on_message_sent(self):
        def decorator(function: Callable):
            def process():
                while True:
                    cache = self.get_messages()
                    time.sleep(0.25)
                    current = self.get_messages()
                    difference = u.difference(current, cache)
                    if len(difference) >= 1:
                        function(messages = difference)
            thread = Thread(target = process)
            thread.start()
        return decorator
    
    def on_player_online(self):
        def decorator(function: Callable):
            def process():
                while True:
                    cache = self.get_playerList()
                    time.sleep(0.1)
                    current = self.get_playerList()
                    difference = u.difference(current, cache)
                    if len(difference) >= 1:
                        function(players = difference)
            thread = Thread(target = process)
            thread.start()
        return decorator
    
    def on_player_offline(self):
        def decorator(function: Callable):
            def process():
                while True:
                    cache = self.get_playerList()
                    time.sleep(0.1)
                    current = self.get_playerList()
                    difference = u.difference(cache, current)
                    if len(difference) >= 1:
                        function(players = difference)
            thread = Thread(target = process)
            thread.start()
        return decorator
    
