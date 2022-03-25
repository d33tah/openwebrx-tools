#!/usr/bin/env python3

import struct
import sys
import datetime


OFFSETS = {
    "SR7PA": 2716,
    "SR7LDZ": 926,
    "SR7LD": 2162,
    "SR7SI": 2049,
}

MIN_SIGNAL_DB = -68
MIN_LENGTH_S = 1


def maybe_log_contact(k, v, ts, contact_since):
    length = (ts - contact_since[v]) if contact_since[v] else 0
    if contact_since[v] is not None and length > MIN_LENGTH_S:
        print(
            k,
            str(datetime.datetime.fromtimestamp(ts)),
            length,
        )


def main():
    fin = open("/dev/stdin", "rb")
    contact_since = {v: None for v in OFFSETS.values()}
    n = 0
    while True:
        ts_b = fin.read(8)
        if len(ts_b) < 8:
            break
        n += 1
        ts = struct.unpack("d", ts_b)[0]
        data = fin.read(4 * 4096)
        floats = struct.unpack("f" * 4096, data)
        for k, v in OFFSETS.items():
            if floats[v] > MIN_SIGNAL_DB:
                if contact_since[v] is None:
                    contact_since[v] = ts
            elif floats[v] < MIN_SIGNAL_DB:
                maybe_log_contact(k, v, ts, contact_since)
                contact_since[v] = None
    for k, v in OFFSETS.items():
        maybe_log_contact(k, v, ts, contact_since)
    sys.stderr.write("%d samples were analyzed.\n" % n)


if __name__ == "__main__":
    main()
