#!/usr/bin/env python3

import struct
import sys
import datetime


OFFSETY = {
    "SR7PA": 2716,
    "SR7LDZ": 926,
}

MIN_SYGNAL_DB = -60
MIN_DLUGOSC_S = 20


def main():
    fin = open("/dev/stdin", "rb")
    lacznosc_od = {v: None for v in OFFSETY.values()}
    n = 0
    while True:
        ts = fin.read(8)
        if len(ts) < 8:
            break
        n += 1
        ts = struct.unpack("d", ts)[0]
        data = fin.read(4 * 4096)
        floats = struct.unpack("f" * 4096, data)
        for k, v in OFFSETY.items():
            if floats[v] > MIN_SYGNAL_DB:
                if lacznosc_od[v] is None:
                    lacznosc_od[v] = ts
            elif floats[v] < MIN_SYGNAL_DB:
                dlugosc = (ts - lacznosc_od[v]) if lacznosc_od[v] else 0
                if lacznosc_od[v] is not None and dlugosc > MIN_DLUGOSC_S:
                    print(
                        k,
                        str(datetime.datetime.fromtimestamp(ts)),
                        dlugosc,
                    )
                lacznosc_od[v] = None
    sys.stderr.write("Przeanalizowano %d probek.\n" % n)


if __name__ == "__main__":
    main()
