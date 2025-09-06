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



import aiohttp
import asyncio
import json
import importlib.resources
import time
import logging
from typing import Callable

from .endpoints import *
from .models import *
from .body import *
from . import utils as u

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Client:

    """
    Asynchronous GeoFS Client with caching, messaging, and event handling.

    This class provides a high-level interface to the GeoFS multiplayer API.
    It abstracts away raw HTTP requests into convenient methods for:
      - Connecting and performing the initial handshake.
      - Querying online players and aircraft.
      - Fetching and sending chat messages.
      - Creating artificial GeoFS server-side clients
      - Registering asynchronous event listeners for player activity and chat.

    Usage:
        client = Client(geofsSessionID, geofsAccountID)
        await client.start()

        # Fetch all players
        players = await client.get_playerList()

        # Send a chat message
        await client.send_message("Hello world!")

        # Register an event handler
        @client.on_message_sent()
        async def handle_messages(messages):
            for msg in messages:
                print(f"{msg.author['callsign']}: {msg.content}")
    """

    CACHE_TTL = 10 
    """Time-to-live for player cache in seconds."""


    def __init__(self, geofsSessionID: str, geofsAccountID: str):

        """
        Initialize a GeoFS client.

        Args:
            geofsSessionID (str): Session ID for the current GeoFS login.
            geofsAccountID (str): GeoFS account ID of the user.

        Note:
            The session ID and account ID are required for chat-related methods.
            If passed as blank, chat will be unavailable but player list queries
            will still function.
        """

        self.sessionID = geofsSessionID
        self.accountID = geofsAccountID
        self.cache: dict[str, Player] = {}
        self.cache_last_updated: float = 0.0
        self.myId: int | None = None
        self.lastMsgId: int | None = None
        self.userCount: int = 0

        self._decorator_tasks: list[asyncio.Task] = []

        # Load aircraft codes once
        with importlib.resources.open_text('geofs.data', 'aircraftcodes.json') as aircraft_raw:
            self.ac_codes = json.load(aircraft_raw)

        # Prepare update body
        self.update_body = update_body.copy()
        self.update_body.update({
            "sid": self.sessionID,
            "acid": self.accountID,
            "id": None,
            "ti": None,
            "ci": None
        })

        # Prepare map body placeholder
        self.map_body = map_body.copy()
        self.map_body["id"] = None

        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self):

        """Create aiohttp.ClientSession if it doesn't exist yet."""

        if self._session is None:
            self._session = aiohttp.ClientSession(cookies={"PHPSESSID": self.sessionID})

    async def handshake(self):

        """
        Perform the handshake with GeoFS servers.

        This initializes `myId`, `lastMsgId`, `userCount`, updates update_body,
        sets map_body["id"], and captures server time in `update_body["ti"]`.

        Raises
        ------
        RuntimeError
            If the handshake fails due to network issues / non-2xx responses.
        """

        await self._ensure_session()
        try:
            logging.info("Performing handshake with GeoFS servers")
            async with self._session.post(update_endpoint, json=self.update_body) as resp:
                resp.raise_for_status()
                hs_response = await resp.json()

            self.myId = hs_response["myId"]
            self.lastMsgId = hs_response["lastMsgId"]
            self.userCount = hs_response["userCount"]

            self.update_body["id"] = self.myId
            self.update_body["ci"] = self.lastMsgId
            self.update_body["ti"] = hs_response["serverTime"]
            self.map_body["id"] = self.myId

            logging.info("GeoFS Client successfully initialized")
        except aiohttp.ClientError as e:
            logging.error(f"Error during handshake: {e}")
            raise RuntimeError("Failed to initialize GeoFS Client. Check connection or credentials.")

    async def _refresh_cache(self):
        
        """
        Refresh the internal player cache by querying the map endpoint.

        Updates:
            - `self.cache` with current online players (ACID → Player).
            - `self.userCount` with the total number of online players.
            - `self.cache_last_updated` with the current timestamp.
        """

        await self._ensure_session()
        try:
            async with self._session.post(map_endpoint, json=self.map_body) as resp:
                resp.raise_for_status()
                data = await resp.json()

            self.userCount = data.get("userCount", 0)
            users = data.get("users", [])
            self.cache = {user['acid']: Player(user) for user in users if user is not None}
            self.cache_last_updated = time.time()
        except aiohttp.ClientError as e:
            logging.error(f"Error refreshing cache: {e}")

    async def get_player(self, acid: str) -> Player | None:
        
        """
        Retrieve a single player by ACID.

        Args:
            acid (str): The player's account ID.

        Returns:
            Player | None: The corresponding Player object if found, otherwise None.
        """

        if self.cache is None or time.time() - self.cache_last_updated > self.CACHE_TTL:
            await self._refresh_cache()
        return self.cache.get(acid)

    async def get_playerList(self) -> list[Player]:

        """
        Retrieve a list of all online players.

        Returns:
            list[Player]: A list of Player objects representing all current users.
        """

        if self.cache is None or time.time() - self.cache_last_updated > self.CACHE_TTL:
            await self._refresh_cache()
        return list(self.cache.values())

    async def get_userCount(self) -> int:

        """
        Retrieve the current number of online users.

        Returns:
            int: Number of users currently online.
        """

        if self.cache is None or time.time() - self.cache_last_updated > self.CACHE_TTL:
            await self._refresh_cache()
        return self.userCount

    async def get_aircraft(self, id: str) -> Aircraft:
        
        """
        Retrieve an aircraft by ID.

        Args:
            id (str): Aircraft ID.

        Returns:
            Aircraft: An Aircraft object with ID and human-readable name.
        """

        id = str(id)
        if id in self.ac_codes:
            return Aircraft({"id": id, "name": self.ac_codes[id]})
        return Aircraft({"id": id, "name": "Unknown"})

    async def get_messages(self) -> list[Message]:
        
        """
        Fetch new chat messages from the server.

        Returns:
            list[Message]: A list of new Message objects since the last query.
        """

        await self._ensure_session()
        self.update_body["ci"] = self.lastMsgId
        self.update_body["id"] = self.myId
        try:
            async with self._session.post(update_endpoint, json=self.update_body) as resp:
                resp.raise_for_status()
                data = await resp.json()

            self.userCount = data.get("userCount", 0)
            self.myId = data.get("myId", self.myId)
            self.lastMsgId = data.get("lastMsgId", self.lastMsgId)
            return [Message(msg) for msg in data.get("chatMessages", [])]
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching messages: {e}")
            return []

    async def update(self):
        
        """
        Update the client state on the GeoFS server.

        This sends a "heartbeat"-style request to keep the session alive and
        update Client.myId and Client.userCount without sending a message.
        """

        await self._ensure_session()
        self.update_body["ci"] = self.lastMsgId
        self.update_body["id"] = self.myId
        try:
            async with self._session.post(update_endpoint, json=self.update_body) as resp:
                resp.raise_for_status()
                data = await resp.json()
            self.userCount = data.get("userCount", self.userCount)
            self.myId = data.get("myId", self.myId)
        except aiohttp.ClientError as e:
            logging.error(f"Error updating client: {e}")

    async def send_message(self, msg: str):
        
        """
        Send a chat message to the GeoFS server.

        Args:
            msg (str): The message text to send.

        Updates:
            - `lastMsgId` to the new last message.
            - `userCount` if the server response includes it.

        Raises:
            aiohttp.ClientError: If sending fails due to network or server error.
        """

        await self._ensure_session()
        msg_body = self.update_body.copy()
        msg_body["m"] = msg
        try:
            async with self._session.post(update_endpoint, json=msg_body) as resp:
                resp.raise_for_status()
                data = await resp.json()
            self.myId = data.get("myId", self.myId)
            self.lastMsgId = data.get("lastMsgId", self.lastMsgId)
            self.userCount = data.get("userCount", self.userCount)
        except aiohttp.ClientError as e:
            logging.error(f"Error sending message: {e}")


    def on_message_sent(self):
        
        """
        Decorator for asynchronous handlers triggered by new chat messages.

        Args:
            interval (float): Polling interval in seconds (default: 0.5).

        Example:
            @client.on_message_sent()
            async def handle_messages(messages):
                for msg in messages:
                    print(f"{msg.author['callsign']}: {msg.content}")
        """

        def decorator(func: Callable):
            async def process():
                while True:
                    messages = await self.get_messages()
                    if messages:
                        await func(messages=messages)
                    await asyncio.sleep(0.5)
            task = asyncio.create_task(process())
            self._decorator_tasks.append(task)
            return func
        return decorator

    def on_player_online(self):
        
        """
        Decorator for asynchronous handlers triggered when players come online.

        Args:
            interval (float): Polling interval in seconds (default: 5.0).

        Example:
            @client.on_player_online()
            async def handle_online(players):
                for p in players:
                    print(f"Player {p.callsign} came online")
        """

        def decorator(func: Callable):
            async def process():
                cache = await self.get_playerList()
                while True:
                    await asyncio.sleep(10)
                    current = await self.get_playerList()
                    difference = u.difference(current, cache)
                    if difference:
                        await func(players=difference)
                    cache = current
            task = asyncio.create_task(process())
            self._decorator_tasks.append(task)
            return func
        return decorator

    def on_player_offline(self):
        
        """
        Decorator for asynchronous handlers triggered when players go offline.

        Args:
            interval (float): Polling interval in seconds (default: 5.0).

        Example:
            @client.on_player_offline()
            async def handle_offline(players):
                for p in players:
                    print(f"Player {p.callsign} went offline")
        """

        def decorator(func: Callable):
            async def process():
                cache = await self.get_playerList()
                while True:
                    await asyncio.sleep(10)
                    current = await self.get_playerList()
                    difference = u.difference(cache, current)
                    if difference:
                        await func(players=difference)
                    cache = current
            task = asyncio.create_task(process())
            self._decorator_tasks.append(task)
            return func
        return decorator

    async def start(self):
        
        """
        Abstracts away Client initializing sequence (handshaking and cache initializing)
        """

        await self.handshake()
        await self._refresh_cache()

    async def close(self):

        """
        Abstracts away Client closing sequence (cancelling async decorators and closing aiohttp.ClientSession)
        """

        for task in self._decorator_tasks:
            task.cancel()
        if self._session:
            await self._session.close()
            self._session = None
