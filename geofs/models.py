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



from urllib.parse import unquote
from . import utils as u



class Aircraft:

    #Represents an aircraft in GeoFS

    def __init__(self, _data: dict):
        self._data = _data
        self.id = self._data["id"]
        self.name = self._data["name"]
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Aircraft):
            return False
        return self.id == __o.id and self.name == __o.name


class Player:

#Represents an online player in GeoFS

    def __init__(self, _data: dict):
        self._data = _data
        self.acid = self._data["acid"]
        self.aircraft = Aircraft(u.get_aircraft(self._data["ac"]))
        self.callsign = self._data["cs"]
        self.foo = self.acid is None
        self.airspeed = self._data["st"]["as"]
        if self._data["co"]:
            self.lat = self._data["co"][0]
            self.long = self._data["co"][1]
            self.alt = round(self._data["co"][2]*3.28084, 3) #Meter to feet conversion
            if self._data["co"][3] < 0:
                self.hdg = round(self._data["co"][3] + 360, 2)
            else:
                self.hdg = round(self._data["co"][3], 2)
            self.pitch = -round(self._data["co"][4], 2)
            self.roll = round(self._data["co"][5], 2)
        else:
            self.lat = None
            self.long = None
            self.alt = None
            self.hdg = None
            self.pitch = None
            self.roll = None
        
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Player):
            return False
        return self.acid == __o.acid   


class Message:

    #Represents a message sent in the GeoFS Chat (author part needs severe optimization)

    def __init__(self, _data: dict):
        self._data = _data
        self.author = Player(u.get_player(self._data["acid"]))
        self.content = unquote(self._data["msg"])

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Message):
            return False
        return self.author == __o.author and self.content == __o.content
    

class Airport:

    #Represents an airport in GeoFS (make it compatible with the more complete airstrip file)

    def __init__(self, _data: dict):
        self._data = _data
        self.icao = self._data["icao"]
        self.lat = self._data["coord"][0]
        self.long = self._data["coord"][1]
        self.cc = self._data["cc"]
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Airport):
            return False
        return self.icao == __o.icao
