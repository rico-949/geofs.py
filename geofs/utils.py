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
from .endpoints import *
from .body import *


def get_aircraft(id: str):
    id = str(id)
    with importlib.resources.open_text('geofs.data', 'aircraftcodes.json') as aircraft_raw:
        ac_codes = json.load(aircraft_raw)
    if id in ac_codes:
        data = {"id": id, "name": ac_codes[id]}
        return data
    return {"id": id, "name": "Unknown"}



     
def difference(list_1: list, list_2: list) -> list:
    set_2 = set(list_2)  
    return [element for element in list_1 if element not in set_2]  

