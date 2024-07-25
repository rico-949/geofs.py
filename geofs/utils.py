import json
import importlib.resources
from .models import Aircraft, Player

def get_aircraft(id):
        with importlib.resources.open_text('geofs.py', 'data/aircraftcodes.json') as file:
            codes = json.load(file)
        if id in codes:
            data = {"id": {id}, "name": data[id]["name"]}
            return data
        else:
            return {"id": {id}, "name": "Unknown"}