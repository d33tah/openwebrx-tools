#!/usr/bin/env python3

import statistics
import struct


def main():
    fin = open("/dev/stdin", "rb")
    transposed = [[] for _ in range(4096)]
    for _ in range(1000):
        ts = fin.read(8)
        if len(ts) < 8:
            break
        data = fin.read(4 * 4096)
        floats = [int(x) for x in struct.unpack("f" * 4096, data)]
        for n, v in enumerate(floats):
            transposed[n].append(v)
    top_indices = [(statistics.stdev(transposed[x]), x) for x in range(4096)]
    top_indices.sort()
    print(top_indices[:-10])
    print(top_indices[10:])


if __name__ == "__main__":
    main()
