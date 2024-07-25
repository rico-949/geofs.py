import urllib.parse
from typing import Iterator, Union
import utils as u



class Aircraft:

    def __init__(self, _data: dict):
        self._data = _data
        self.id = self._data["id"]
        self.name = self._data["name"]
    
    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)




class Player:

#Represents an online player in GeoFS
#The data is the dictionary the map_endpoint (refer to endpoints.py) returns for each player as a list

    def __init__(self, _data: dict):
        self._data = _data
        self.acid = self._data["acid"]
        self.aircraft = Aircraft(u.get_aircraft(self._data["ac"]))
        self.callsign = self._data["cs"]
        self.foo = self.acid is None
        self.airspeed = self._data["st"]["as"]
        self.lat = self._data["co"][0]
        self.long = self._data["co"][1]
        self.altitude = round(self._data["co"][2]*3.28084, 3)
        if self._data["co"][3] < 0:
            self.hdg = round(self._data["co"][3] + 360, 2)
        else:
            self.hdg = round(self._dat["co"][3], 2)
        

