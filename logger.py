from websocket import create_connection
import struct
import time
import logging

f = open(f"log_{time.time()}.bin", "wb")
while True:
    try:
        ws = create_connection("ws://192.168.1.134:8073/ws/")
        ws.send("SERVER DE CLIENT client=openwebrx.js type=receiver")
        ws.send(
            """{
              "type": "connectionproperties",
              "params": {
                "output_rate": 11025,
                "hd_output_rate": 44100
              }
            }"""
        )
        ws.send(
            """{
          "type": "dspcontrol",
          "params": {
            "low_cut": -4000,
            "high_cut": 4000,
            "offset_freq": -400000,
            "mod": "nfm",
            "dmr_filter": 3,
            "squelch_level": -50,
            "secondary_mod": false
          }
        }"""
        )
        ws.send(
            """{
          "type": "dspcontrol",
          "action": "start"
        }"""
        )
        ws.send(
            """{
          "type": "dspcontrol",
          "params": {
            "secondary_offset_freq": 1000
          }
        }"""
        )

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
