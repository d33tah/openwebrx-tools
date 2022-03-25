#!/usr/bin/env python3

import datetime
import struct
import time
import logging

import yaml
import telegram
import websocket

OFFSETS = {
    "SR7PA": 2716,
    "SR7LDZ": 926,
    "SR7LD": 2162,
    "SR7SI": 2049,
}

MIN_SIGNAL_DB = -68
MIN_LENGTH_S = 20


def maybe_log_contact(bot, config, k, v, ts, contact_since):
    length = (ts - contact_since[v]) if contact_since[v] else 0
    if contact_since[v] is not None and length > MIN_LENGTH_S:
        msg = " ".join([k, str(datetime.datetime.fromtimestamp(ts)), length])
        bot.send_message(text=msg, chat_id=config["tgchatid"])


def main():
    config = yaml.load(open("config.yaml"), Loader=yaml.SafeLoader)
    bot = telegram.Bot(config["tgkey"])
    bot.send_message(text="hello, world", chat_id=config["tgchatid"])
    contact_since = {v: None for v in OFFSETS.values()}
    while True:
        try:
            ws = websocket.create_connection("ws://192.168.1.134:8073/ws/")
            ws.send("SERVER DE CLIENT client=openwebrx.js type=receiver")
            ts = time.time()
            while True:
                msg = ws.recv()
                if type(msg) != bytes:
                    continue
                if msg[0] != 1:
                    continue
                data = msg[1:]
                floats = struct.unpack("f" * 4096, data)
                for k, v in OFFSETS.items():
                    if floats[v] > MIN_SIGNAL_DB:
                        if contact_since[v] is None:
                            contact_since[v] = ts
                    elif floats[v] < MIN_SIGNAL_DB:
                        maybe_log_contact(bot, config, k, v, ts, contact_since)
                        contact_since[v] = None
            ws.close()
        except Exception as e:
            logging.exception(e)


if __name__ == "__main__":
    main()
