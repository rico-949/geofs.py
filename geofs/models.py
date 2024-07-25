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
import utils as u



class Aircraft:

    #Represents an aircraft in GeoFS

    def __init__(self, _data: dict):
        self._data = _data
        self.id = self._data["id"]
        self.name = self._data["name"]
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Aircraft):
            return False
        return list(self) == list(__o)


class Player:

#Represents an online player in GeoFS

    def __init__(self, _data: dict):
        self._data = _data
        self.acid = self._data["acid"]
        self.aircraft = u.get_aircraft(self._data["ac"])
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
        
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Player):
            return False
        return self.acid == __o.acid   


class Message:

    #Represents a message sent in the GeoFS Chat

    def __init__(self, _data: dict):
        self._data = _data
        self.author = u.get_player(self._data["acid"])
        self.content = unquote(self._data["msg"])

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Message):
            return False
        return list(self) == list (__o)