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
import math


class Aircraft:

    """
    Represents an aircraft in GeoFS.

    Attributes
    ----------
    id : str
        The aircraft's unique identifier (as defined in GeoFS).
    name : str
        The aircraft's display name.

    Notes
    -----
    This class is a lightweight wrapper around the aircraft
    dictionary returned by GeoFS servers.
    """

    def __init__(self, _data: dict):

        """
        Initialize an Aircraft object.

        Parameters
        ----------
        _data : dict
            Dictionary containing aircraft data, with keys:
            - "id": str
            - "name": str
        """

        self._data = _data
        self.id = self._data["id"]
        self.name = self._data["name"]
    
    def __eq__(self, __o: object) -> bool:

        """
        Compare two Aircraft objects for equality.

        Parameters
        ----------
        __o : object
            Object to compare against.

        Returns
        -------
        bool
            True if both Aircraft have the same ID and name, else False.
        """
         
        if not isinstance(__o, Aircraft):
            return False
        return self.id == __o.id and self.name == __o.name



class Player:
    
    """
    Represents an online player in GeoFS.

    Attributes
    ----------
    acid : str
        The player's GeoFS account ID.
    id : int
        The player's session ID.
    gears : bool
        Whether the aircraft landing gears are deployed.
    aircraft : Aircraft
        The player's current aircraft object.
    callsign : str
        The player's callsign.
    foo : bool
        True if the callsign is exactly "Foo".
    airspeed : float
        The player's indicated airspeed.
    lat : float
        Latitude in decimal degrees.
    long : float
        Longitude in decimal degrees.
    alt : float
        Altitude in feet (converted from meters).
    hdg : float
        Heading in degrees, normalized to [0, 360).
    pitch : float
        Aircraft pitch angle.
    roll : float
        Aircraft roll angle.
    x_velocity : float
        X-axis velocity.
    y_velocity : float
        Y-axis velocity.
    z_velocity : float
        Z-axis velocity.
    x_angular_mom : float
        Angular momentum around X-axis.
    y_angular_mom : float
        Angular momentum around Y-axis.
    z_angular_mom : float
        Angular momentum around Z-axis.

    Notes
    -----
    If position or velocity data are missing, malformed, or invalid
    (NaN/Infinity), all positional/velocity attributes are set to NaN.
    """

    def __init__(self, _data: dict):

        """
        Initialize a Player object.

        Parameters
        ----------
        _data : dict
            Dictionary containing player data from GeoFS, typically with keys:
            - "acid": str
            - "id": int
            - "st": dict (state, including "gr" for gear, "as" for airspeed)
            - "ac": str (aircraft ID)
            - "cs": str (callsign)
            - "co": list[float] (coordinates and orientation)
            - "ve": list[float] (velocities and angular momenta)
        """

        self._data = _data
        self.acid = self._data["acid"]
        self.id = self._data["id"]
        self.gears = bool(self._data["st"]["gr"])
        self.aircraft = Aircraft(u.get_aircraft(self._data["ac"]))
        self.callsign = self._data["cs"]
        self.foo = self.callsign == "Foo"
        self.airspeed = self._data["st"]["as"]

        self.co = self._data["co"]
        self.ve = self._data["ve"]
        

        if (
            isinstance(self.co, list)
            and len(self.co) == 6
            and all(isinstance(x, (int, float)) for x in self.co)
            and not any(math.isnan(x) or math.isinf(x) for x in self.co)
            and isinstance(self.ve, list)
            and len(self.ve) == 6
            and all(isinstance(x, (int, float)) for x in self.ve)
            and not any(math.isnan(x) or math.isinf(x) for x in self.ve)
        ):
            self.lat = float(self.co[0])
            self.long = float(self.co[1])
            self.alt = float(self.co[2]) * 3.28084  # Convert meters to feet

            # Normalize heading to [0, 360)
            self.hdg = float(self.co[3] % 360)
            self.pitch = float(self.co[4])
            self.roll = float(self.co[5])
            self.x_velocity = self.ve[0]
            self.y_velocity = self.ve[1]
            self.z_velocity = self.ve[2]

            self.x_angular_mom = self.ve[3]
            self.y_angular_mom = self.ve[4]
            self.z_angular_mom = self.ve[5]
            
        else:
            # Fallback to NaN if invalid or malformed
            self.lat = float('nan')
            self.long = float('nan')
            self.alt = float('nan')
            self.hdg = float('nan')
            self.pitch = float('nan')
            self.roll = float('nan')

            self.x_velocity = float('nan')
            self.y_velocity = float('nan')
            self.z_velocity = float('nan')

            self.x_angular_mom = float('nan')
            self.y_angular_mom = float('nan')
            self.z_angular_mom = float('nan')

    def __eq__(self, __o: object) -> bool:

        """
        Compare two Player objects for equality.

        Parameters
        ----------
        __o : object
            Object to compare against.

        Returns
        -------
        bool
            True if both players share the same account ID, else False.
        """

        if not isinstance(__o, Player):
            return False
        return self.acid == __o.acid



class Message:

    """
    Represents a message sent in the GeoFS chat.

    Attributes
    ----------
    author : dict
        Information about the message author:
        - "acid": str (author's account ID)
        - "callsign": str (author's callsign)
    content : str
        Decoded message content.
    """

    def __init__(self, _data: dict):

        """
        Initialize a Message object.

        Parameters
        ----------
        _data : dict
            Dictionary containing message data from GeoFS, with keys:
            - "acid": str
            - "cs": str (callsign)
            - "msg": str (URL-encoded message content)
        """

        self._data = _data
        self.author = {
            "acid": self._data["acid"],
            "callsign": self._data["cs"]
        }
        self.content = unquote(self._data["msg"])

    def __eq__(self, __o: object) -> bool:

        """
        Compare two Message objects for equality.

        Parameters
        ----------
        __o : object
            Object to compare against.

        Returns
        -------
        bool
            True if both author and content match, else False.
        """
        
        if not isinstance(__o, Message):
            return False
        return self.author == __o.author and self.content == __o.content
    

