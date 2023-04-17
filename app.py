import asyncio
import http
import signal
import json

import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"

async def receive(websocket):
    ws = websocket
    await listen_event(ws)
    await event("connect")
    try:
        while True:
            data = await ws.recv()
            await parse_command(json.loads(data))
    except (websockets.exceptions.ConnectionClosedOK,websockets.exceptions.ConnectionClosedError,websockets.exceptions.ConnectionClosed):
        #await self.event("disconnect")  # self.event_disconnect()
        #sys.exit()
        pass

async def listen_event(ws):
    events = []
    for event in events:
        await ws.send(json.dumps({
            "body": {"eventName": event},
            "header": {
            "requestId": "00000000-0000-0000-0000-000000000000",
            "messagePurpose": "subscribe",
            "version": 1,
            "messageType": "commandRequest"}
            }))

async def parse_command(message):
        
    if message["header"]["messagePurpose"] == "event":
        event_name = message["header"]["eventName"]
        await event(event_name, message)

        if message["header"]["eventName"] == "PlayerMessage" and message["body"]["type"] == 'chat':
            pass

    elif message["header"]["messagePurpose"] == "error":
        await event("error", message)

async def event(name, *args):
    func = f"event_{name}"
    if not func == "event_connect":
        func = f"event_test"

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

async def event_connect():
    mcresptext = "§a[Server]§r welcome!"
    #await self.command('tellraw @a {"rawtext":[{"text":"'+mcresptext+'"}]} ')
    print("Connected!")

async def event_test(event):
    print(event)
    pass

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


if __name__ == "__main__":
    asyncio.run(main())