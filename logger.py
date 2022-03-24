from websocket import create_connection
import struct
import time
import logging

f = open(f"log_{time.time()}.bin", "wb")
while True:
    try:
        ws = create_connection("ws://192.168.1.134:8073/ws/")
        ws.send("SERVER DE CLIENT client=openwebrx.js type=receiver")
        n = 0
        t = time.time()
        while True:
            msg = ws.recv()
            if type(msg) != bytes:
                continue
            if msg[0] != 1:
                continue
            data = msg[1:]
            f.write(struct.pack("d", time.time()))
            f.write(data)
            f.flush()
        ws.close()
    except Exception as e:
        logging.exception(e)
