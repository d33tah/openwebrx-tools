#!/usr/bin/env python3

import sys
import signal
import datetime
import struct
import time
import logging
import atexit
import urllib.request

import yaml
import telegram
import websocket

OFFSETS = {
    "SR7PA": 2716,
    "SR7LDZ": 926,
    "SR7LD": 2162,
    "SR7SI": 2049,
}

MIN_SIGNAL_DB = -65
MIN_LENGTH_S = 2


def maybe_log_contact(
    bot, config, k, v, ts, contact_since, is_logged, last_logged
):
    length = (ts - contact_since[v]) if contact_since[v] else 0
    if last_logged[v] is not None:
        if ts - last_logged[v] > 10:
            logged_long_ago = True
        else:
            logged_long_ago = False
    else:
        logged_long_ago = True

    if (
        not is_logged[v]
        and contact_since[v] is not None
        and length > MIN_LENGTH_S
        and logged_long_ago
    ):
        msg = " ".join(
            [str(x) for x in [k, datetime.datetime.fromtimestamp(ts), length]]
        )
        bot.send_message(text=msg, chat_id=config["tgchatid"])
        is_logged[v] = True
        last_logged[v] = ts


def get_atexit(bot, config):
    def atexit_handler(*args, **kwargs):
        bot.send_message(
            text="Bot shut down. If that's not expected, please check logs.",
            chat_id=config["tgchatid"],
        )
        sys.exit(0)

    return atexit_handler


def main():
    config = yaml.load(open("config.yaml"), Loader=yaml.SafeLoader)
    bot = telegram.Bot(config["tgkey"])
    exit_handler = get_atexit(bot, config)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    atexit.register(get_atexit(bot, config))
    myip = urllib.request.urlopen("https://ifconfig.me/ip").read().decode()
    bot.send_message(
        text="Bot restarted. Host IP is: %s" % myip,
        chat_id=config["tgchatid"],
    )
    # time.sleep(10.0)
    print("Startup initiated.")
    contact_since = {v: None for v in OFFSETS.values()}
    is_logged = {v: False for v in OFFSETS.values()}
    last_logged = {v: None for v in OFFSETS.values()}
    while True:
        try:
            ws = websocket.create_connection("ws://192.168.1.134:8073/ws/")
            ws.send("SERVER DE CLIENT client=openwebrx.js type=receiver")
            while True:
                ts = time.time()
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
                        else:
                            maybe_log_contact(
                                bot,
                                config,
                                k,
                                v,
                                ts,
                                contact_since,
                                is_logged,
                                last_logged,
                            )
                    elif floats[v] < MIN_SIGNAL_DB:
                        maybe_log_contact(
                            bot,
                            config,
                            k,
                            v,
                            ts,
                            contact_since,
                            is_logged,
                            last_logged,
                        )
                        contact_since[v] = None
                        is_logged[v] = False
            ws.close()
        except Exception as e:
            logging.exception(e)


if __name__ == "__main__":
    main()
