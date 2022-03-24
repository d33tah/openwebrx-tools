#!/usr/bin/env python3

import sys
import math
import base64
import struct

WATERFALL_MIN_LEVEL = -88
WATERFALL_MAX_LEVEL = -20

WATERFALL_COLORS = [
    list(base64.b16decode(x))
    for x in [
        "000000",
        "0000FF",
        "00FFFF",
        "00FF00",
        "FFFF00",
        "FF0000",
        "FF00FF",
        "FFFFFF",
    ]
]


def color_between(first, second, percent):
    return [
        int(first[0] + percent * (second[0] - first[0])),
        int(first[1] + percent * (second[1] - first[1])),
        int(first[2] + percent * (second[2] - first[2])),
    ]


def waterfall_mkcolor(db_value):
    value_percent = (db_value - WATERFALL_MIN_LEVEL) / (
        WATERFALL_MAX_LEVEL - WATERFALL_MIN_LEVEL
    )
    value_percent = max(0, min(1, value_percent))

    scaled = value_percent * (len(WATERFALL_COLORS) - 1)
    index = math.floor(scaled)
    remain = scaled - index
    if remain == 0:
        return WATERFALL_COLORS[index]
    return color_between(
        WATERFALL_COLORS[index], WATERFALL_COLORS[index + 1], remain
    )


def main():
    nsamples = 1000
    print("P3")
    print("4096 " + str(nsamples))
    print("256")
    fin = open("/dev/stdin", "rb")
    for _ in range(nsamples):
        ts = fin.read(8)
        if len(ts) < 8:
            break
        data = fin.read(4 * 4096)
        floats = [
            waterfall_mkcolor(x) for x in struct.unpack("f" * 4096, data)
        ]
        for x in floats:
            print(" ".join([str(n) for n in x]))


if __name__ == "__main__":
    main()
