# geofs.py

An asynchronous Python client library for interacting with the GeoFS
multiplayer servers.\
Provides access to player data, chat messages, aircraft information, and
supports event-driven decorators.

------------------------------------------------------------------------

## Features

-   Asynchronous client with built-in caching.
-   Retrieve online players and aircraft details.
-   Fetch and send chat messages.
-   Event decorators for reacting to player activity and messages.
-   Structured models for Aircraft, Player, and Message entities.

------------------------------------------------------------------------


## Usage Example

``` python
import asyncio
from geofs.client import Client

async def main():
    client = Client(geofsSessionID="YOUR_SESSION_ID", geofsAccountID="YOUR_ACCOUNT_ID")
    await client.start()

    # Fetch all players
    players = await client.get_playerList()
    for p in players:
        print(p.callsign, p.lat, p.long)

    # Send a message
    await client.send_message("Hello GeoFS!")

    await client.close()

asyncio.run(main())
```

------------------------------------------------------------------------

## Client API

### `class Client`

Asynchronous GeoFS Client with caching, messaging, and event handling.

**Initialization**

``` python
Client(geofsSessionID: str, geofsAccountID: str)
```

-   `geofsSessionID` : Session ID cookie from GeoFS.
-   `geofsAccountID` : GeoFS account ID.

**Key Methods**

-   `async handshake()`\
    Initialize client with the GeoFS server.

-   `async get_player(acid: str) -> Player | None`\
    Return a `Player` object by ACID, refreshing cache if necessary.

-   `async get_playerList() -> list[Player]`\
    Return a list of all Player objects.

-   `async get_userCount() -> int`\
    Return the current number of users.

-   `async get_aircraft(id: str) -> Aircraft`\
    Return an `Aircraft` object by ID.

-   `async get_messages() -> list[Message]`\
    Fetch new chat messages from server.

-   `async update()`\
    Update client state in server without sending messages.

-   `async send_message(msg: str)`\
    Send a chat message to the server.

-   `def on_message_sent()`\
    Async decorator for reacting to incoming messages.

-   `def on_player_online()`\
    Async decorator for detecting players coming online.

-   `def on_player_offline()`\
    Async decorator for detecting players going offline.

-   `async start()`\
    Start client by performing handshake and initializing cache.

-   `async close()`\
    Close client by shutting down session and background tasks.

------------------------------------------------------------------------

## Models

### `class Aircraft`

Represents an aircraft in GeoFS.

**Attributes** - `id : str` --- Aircraft ID. - `name : str` --- Aircraft
display name.

------------------------------------------------------------------------

### `class Player`

Represents an online player in GeoFS.

**Attributes** - `acid : str` --- GeoFS account ID. - `id : int` ---
Player session ID. - `gears : bool` --- Landing gear state. -
`aircraft : Aircraft` --- Current aircraft object. - `callsign : str`
--- Player callsign. - `foo : bool` --- Whether the callsign is
`"Foo"`. - `airspeed : float` --- Indicated airspeed. - `lat : float`
--- Latitude in degrees. - `long : float` --- Longitude in degrees. -
`alt : float` --- Altitude in feet (converted from meters). -
`hdg : float` --- Heading in degrees, normalized to \[0, 360). -
`pitch : float` --- Pitch angle. - `roll : float` --- Roll angle. -
`x_velocity, y_velocity, z_velocity : float` --- Linear velocities. -
`x_angular_mom, y_angular_mom, z_angular_mom : float` --- Angular
momenta.

Invalid or malformed positional/velocity data results in all values
being set to NaN.

------------------------------------------------------------------------

### `class Message`

Represents a chat message in GeoFS.

**Attributes** - `author : dict` --- Author information (`acid`,
`callsign`). - `content : str` --- Decoded message content.

------------------------------------------------------------------------

## License

MIT License
