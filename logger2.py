#!/usr/bin/python3

import math
import base64

from websocket import create_connection


class ImaAdpcmCodec:
    def __init__(self):
        self.reset()

    def reset(self):
        self.stepIndex = 0
        self.predictor = 0
        self.step = 0

    imaIndexTable = [-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8]
    imaStepTable = [
        7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
        19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
        50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
        130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
        337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
        876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
        2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
        5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
        15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767
    ]  # fmt: skip

    def decodeNibble(self, nibble):
        self.stepIndex += ImaAdpcmCodec.imaIndexTable[nibble]
        self.stepIndex = min(max(self.stepIndex, 0), 88)

        diff = self.step >> 3
        if nibble & 1:
            diff += self.step >> 2
        if nibble & 2:
            diff += self.step >> 1
        if nibble & 4:
            diff += self.step
        if nibble & 8:
            diff = -diff

        self.predictor += diff
        self.predictor = min(max(self.predictor, -32768), 32767)

        self.step = ImaAdpcmCodec.imaStepTable[self.stepIndex]

        return self.predictor


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
        return [str(x) for x in WATERFALL_COLORS[index]]
    return color_between(
        WATERFALL_COLORS[index], WATERFALL_COLORS[index + 1], remain
    )


def main(url, nsamples):

    print("P3")
    print("16394 " + str(nsamples))
    print("256")
    ws = create_connection(url)
    ws.send("SERVER DE CLIENT client=openwebrx.js type=receiver")
    n = 0
    while n < nsamples:
        msg = ws.recv()
        if type(msg) != bytes:
            continue
        if msg[0] != 1:
            continue
        data = msg[1:]
        fft = ImaAdpcmCodec()
        for b in data:
            col = waterfall_mkcolor(fft.decodeNibble(b & 0x0F) / 100.0)
            print(" ".join([str(x) for x in col]))
            col = waterfall_mkcolor(fft.decodeNibble((b >> 4) & 0x0F) / 100.0)
            print(" ".join([str(x) for x in col]))
        n += 1
    ws.close()


if __name__ == "__main__":
    main(url="wss://1.websdr.jestok.com/ws/", nsamples=10)
