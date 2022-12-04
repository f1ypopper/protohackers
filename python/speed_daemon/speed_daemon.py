import asyncio
import time
import logging
from asyncio import Queue
PROXY = "0.0.0.0"
PROXY_PORT = 5000
cameras = dict()
dispatchers = dict()
road_limits = dict()

class Car:
    def __init__(self, plate, road, timestamp, mile):
        self.plate = plate
        self.road = road
        self.timestamp = timestamp
        self.mile = mile
    
async def read_string(reader: asyncio.StreamReader):
    str_len = int(await reader.readexactly(8))
    string = await reader.readexactly(str_len)
    return string.decode()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

    heart_beat_task = None

    async def disconnect():
        pass

    async def heart_beat(interval):
        start = time.time()
        while True:
            if time.time() - start >= interval:
                writer.write((65).to_bytes(1, 'big'))

    async def handle_camera_client(road, mile, limit):
        while not reader.at_eof():
            msg_type = await reader.readexactly(8)
            if msg_type == 0x20: #Plate
                plate = await read_string(reader)
                timestamp = await reader.readexactly(32)
                car = Car(plate, road, timestamp, mile)
                if road not in dispatchers:
                    dispatchers[road] = Queue()
                dispatchers[road].put_no_wait(car)

            elif msg_type == 0x40:#WantHeartBeat
                if heart_beat:
                    logging.error("want_heart_beat msg had been already sent")
                    await disconnect()
                    return 
                interval = int(await reader.readexactly(32))/10
                heart_beat_task = asyncio.create_task(heart_beat(interval))
            else:
                logging.error(f"unknown msg {msg_type}")
                await disconnect()

    async def check_for_heart_beat_msg():
        while True:
            msg_type = int(await reader.readexactly(8))
            if msg_type == 0x40:
                if heart_beat:
                    logging.error("want_heart_beat msg had been already sent")
                    await disconnect()
                    return
                interval = int(await reader.readexactly(32))/10
                heart_beat_task = asyncio.create_task(heart_beat(interval))
            else: 
                logging.error(f"unknown msg {msg_type}")
                await disconnect()

    async def handle_dispatcher_client(roads):
        cars = dict()

        t = asyncio.create_task(check_for_heart_beat_msg())
        while True:
            for road in roads:
                if road not in dispatchers:
                    dispatchers[road] = Queue()
                else:
                    queue = dispatchers[road]
                    if not queue.empty():
                        car = await queue.get()
                        if car.plate in cars:
                            mile1 = cars[car.plate].mile
                            mile2 = car.mile
                            timestamp1 = cars[car.plate].timestamp
                            timestamp2 = car.timestamp
                            t  = abs(timestamp1-timestamp2)
                            d = abs(mile1-mile2)
                            speed = d/t
                            if speed - road_limits[road] >= 0.5:
                                #TODO: can implement struct packing to reduce calls?
                                logging.info(f"{car.plate} speeding on road {road} at {speed} mph!")
                                writer.write(len(car.plate).to_bytes(1,'big'))
                                writer.write(car.plate.encode())
                                writer.write(mile1.to_bytes(2,'big'))
                                writer.write(timestamp1.to_bytes(4,'big'))
                                writer.write(mile2.to_bytes(2,'big'))
                                writer.write(timestamp2.to_bytes(4,'big'))
                                writer.write((speed*100).to_bytes(2, 'big'))
                                await writer.drain()
                        else:
                            cars[car.plate] = car

    client_type = int(await reader.readexactly(8))

    if client_type == 0x80:
        logging.info("camera client connected!")
        road = await reader.readexactly(16)
        mile = await reader.readexactly(16)
        limit = await reader.readexactly(16) #miles per hour
        await handle_camera_client(road, mile, limit)
    elif client_type == 0x81:
        logging.info("ticket dispatcher client connected!")
        numroads = int(await reader.readexactly(8))
        roads = []
        for _ in range(0, numroads):
            roads.append(await reader.readexactly(16))
        await handle_dispatcher_client(roads)
    else:
        logging.info(f"unknown client {client_type}?")

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())