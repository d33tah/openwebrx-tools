#!/usr/bin/env python3

import struct
import sys
import datetime


OFFSETY = {
    "SR7PA": 2716,
    "SR7LDZ": 926,
    "SR7LD": 2162,
    "SR7SI": 2049,
}

MIN_SYGNAL_DB = -68
MIN_DLUGOSC_S = 20


def moze_wyswietl_lacznosc(k, v, ts, lacznosc_od):
    dlugosc = (ts - lacznosc_od[v]) if lacznosc_od[v] else 0
    if lacznosc_od[v] is not None and dlugosc > MIN_DLUGOSC_S:
        print(
            k,
            str(datetime.datetime.fromtimestamp(ts)),
            dlugosc,
        )


def main():
    fin = open("/dev/stdin", "rb")
    lacznosc_od = {v: None for v in OFFSETY.values()}
    n = 0
    while True:
        ts_b = fin.read(8)
        if len(ts_b) < 8:
            break
        n += 1
        ts = struct.unpack("d", ts_b)[0]
        data = fin.read(4 * 4096)
        floats = struct.unpack("f" * 4096, data)
        for k, v in OFFSETY.items():
            if floats[v] > MIN_SYGNAL_DB:
                if lacznosc_od[v] is None:
                    lacznosc_od[v] = ts
            elif floats[v] < MIN_SYGNAL_DB:
                moze_wyswietl_lacznosc(k, v, ts, lacznosc_od)
                lacznosc_od[v] = None
    for k, v in OFFSETY.items():
        moze_wyswietl_lacznosc(k, v, ts, lacznosc_od)
    sys.stderr.write("Przeanalizowano %d probek.\n" % n)


if __name__ == "__main__":
    main()
