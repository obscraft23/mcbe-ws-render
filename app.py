import asyncio
import http
import signal
import json

import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

class WsServer:
    def start(self,host="0.0.0.0",port=19132):
        self.host = host
        self.port = port
        asyncio.run(self.main())
        """
        self.ws = websockets.serve(self.receive, self.host, self.port, process_request=self.health_check)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.ws)
        self.loop.run_forever()
        """
    
    async def main(self):
        self.loop = asyncio.get_running_loop()
        self.stop = self.loop.create_future()
        self.loop.add_signal_handler(signal.SIGTERM, self.stop.set_result, None)
        async with websockets.serve(
            self.receive,
            host=self.host,
            port=self.port,
            process_request=self.health_check,
        ):
            await self.stop

    async def health_check(self,path, request_headers):
        if path == "/healthz":
            return http.HTTPStatus.OK, [], b"OK\n"

    async def receive(self,websocket):
        self.ws = websocket
        await self.listen_event()
        await self.event("connect")
        print("test")
        try:
            while True:
                data = await self.ws.recv()
                await self.parse_command(json.loads(data))
        except (websockets.exceptions.ConnectionClosedOK,websockets.exceptions.ConnectionClosedError,websockets.exceptions.ConnectionClosed):
            #await self.event("disconnect")  # self.event_disconnect()
            #sys.exit()
            pass

    async def listen_event(self):
        events = ["PlayerMessage"]
        for event in events:
            await self.ws.send(json.dumps({
                "body": {"eventName": event},
                "header": {
                "requestId": "00000000-0000-0000-0000-000000000000",
                "messagePurpose": "subscribe",
                "version": 1,
                "messageType": "commandRequest"}
                }))

    async def command(self, cmd):
        uuid4 = str(uuid.uuid4())
        cmd_json = json.dumps({
            "body": {"origin": {"type": "player"},"commandLine": cmd,"version": 1},
            "header": {"requestId": uuid4,"messagePurpose": "commandRequest","version": 1,"messageType": "commandRequest"}
        })
    
        await self.ws.send(cmd_json)
        data = await self.ws.recv()
        msg = json.loads(data)
        if msg["header"]["messagePurpose"] == "commandResponse" and msg["header"]["requestId"] == uuid4:
            return msg
        else:
            return None

    async def parse_command(self,message):
            
        if message["header"]["messagePurpose"] == "event":
            event_name = message["header"]["eventName"]
            await self.event(event_name, message)

            if message["header"]["eventName"] == "PlayerMessage" and message["body"]["type"] == 'chat':
                pass

        elif message["header"]["messagePurpose"] == "error":
            await self.event("error", message)

    async def event(self, name, *args):
        func = f"self.event_{name}"
        if not func == "self.event_connect":
            func = f"self.event_test"

        if args == ():
            try:
                await eval(f"{func}()")
            except NameError as e:
                print(f"event_{name}")

        else:
            try:
                await eval(f"{func}({args})")
            except NameError as e:
                print(f"event_{name}")

    async def event_connect(self):
        mcresptext = "§a[Server]§r welcome!"
        await self.command('tellraw @a {"rawtext":[{"text":"'+mcresptext+'"}]} ')
        print("Connected!")

    async def event_test(self,event):
        print(event)
        pass

"""
    async def main():
        # Set the stop condition when receiving SIGTERM.
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        async with websockets.serve(
            receive,
            host="0.0.0.0",
            port=19132,
            process_request=health_check,
        ):
            await stop
"""


if __name__ == "__main__":
    myobj = WsServer()
    myobj.start()