import struct
import click
import numpy as np
import cv2 as cv
import os
import sys
import math


def _read(file, fmt, size=None):
    if size is None:
        size = struct.calcsize(fmt)

    return struct.unpack(fmt, file.read(size))


class PixelFormat:
    def __init__(self, size, flags, fourcc, rgbbitcount, rbitmask, gbitmask, bbitmask, abitmask):
        self.size = size
        self.flags = flags
        self.fourcc = fourcc.to_bytes(4, "little").decode()
        self.rgbbitcount = rgbbitcount
        self.rbitmask = rbitmask
        self.gbitmask = gbitmask
        self.bbitmask = bbitmask
        self.abitmask = abitmask
    
    def __str__(self):
        return f'PixelFormat(size={self.size}, flags={self.flags}, fourcc={self.fourcc}, rgbbitcount={self.rgbbitcount}, rbitmask={self.rbitmask}, gbitmask={self.gbitmask}, bbitmask={self.bbitmask}, abitmask={self.abitmask})'


class DdsHeader:
    def __init__(self, size, flags, height, width, pitch_or_linear_size, depth, mip_map_count, spf, caps, caps2, caps3, caps4):
        self.size = size
        self.flags = flags
        self.height = height
        self.width = width
        self.pitch_or_linear_size = pitch_or_linear_size
        self.depth = depth
        self.mip_map_count = mip_map_count
        self.spf = spf
        self.caps = caps
        self.caps2 = caps2
        self.caps3 = caps3
        self.caps4 = caps4

    @staticmethod
    def load(file):
        pre = _read(file, 'IIIIIII')
        reserved1 = file.read(4*11)
        pf = PixelFormat(*_read(file, 'IIIIIIII'))
        caps = _read(file, 'IIII')
        reserved2 = file.read(4)
        return DdsHeader(*pre, pf, *caps)


class DdsHeaderDxt10:
    def __init__(self, format, dimensions, misc_flag, arraySize, misc_flags2):
        self.format = format
        self.dimensions = dimensions
        self.misc_flag = misc_flag
        self.arraySize = arraySize
        self.misc_flags2 = misc_flags2

    @staticmethod
    def load(file):
        return DdsHeaderDxt10(*_read(file, 'IIIII'))

def color565(data):
    c = int.from_bytes(data, 'little')
    # print(bin(c))
    b, g, r = [c & 0b11111, (c >> 5) & 0b111111, (c >> 11) & 0b11111]
    # print(bin(r), bin(g), bin(b))
    return np.array([b, g, r], dtype='uint32') * 256 // np.array([32, 64, 32])

def do_bc1(image, data):
    w, h, _ = image.shape
    i = 0
    for tx in range(w // 4):
        for ty in range(h // 4):
            color_0 = color565(data[i:i+2])
            color_1 = color565(data[i+2:i+4])
            i += 4
            colors = [
                color_0,
                color_1,
                (2 * color_0 + 1 * color_1) // 3,
                (1 * color_0 + 2 * color_1) // 3,
            ]
            # print(colors)
            for m in range(0, 4):
                k = data[i]
                i += 1
                for n in range(0, 4):
                    v = k & 3
                    k = k >> 2
                    image[tx*4 + m, ty*4 + n, :] = colors[v].astype('uint8')

def do_bc4(image, data):
    w, h = image.shape
    i = 0
    for tx in range(w // 4):
        for ty in range(h // 4):
            red_0 = data[i]
            red_1 = data[i + 1]
            i += 2
            if red_0 > red_1:
                colors = [
                    red_0,
                    red_1,
                    int((6 * red_0 + 1 * red_1) / 7),
                    int((5 * red_0 + 2 * red_1) / 7),
                    int((4 * red_0 + 3 * red_1) / 7),
                    int((3 * red_0 + 4 * red_1) / 7),
                    int((2 * red_0 + 5 * red_1) / 7),
                    int((1 * red_0 + 6 * red_1) / 7),
                ]
            else:
                colors = [
                    red_0,
                    red_1,
                    int((4 * red_0 + 1 * red_1) / 5),
                    int((3 * red_0 + 2 * red_1) / 5),
                    int((2 * red_0 + 3 * red_1) / 5),
                    int((1 * red_0 + 4 * red_1) / 5),
                    0,
                    255
                ]
            for zz in range(0, 4, 2):
                k = (data[i + 2] << 16) | (data[i + 1] << 8) | (data[i])
                # print(bin(k))
                i += 3
                for m in range(zz, zz + 2):
                    for n in range(0, 4):
                        v = k & 7
                        # print(m, n, bin(v))
                        k = k >> 3
                        # if tx*4 + n < w and ty*4 + m < h:
                        image[tx*4 + m, ty*4 + n] = colors[v]

def extract(file, target):
    magic = file.read(4)
    if magic != b'DDS ':
        print(target, magic)
        return

    header = DdsHeader.load(file)
    fmt = header.spf.fourcc
    if fmt == 'DX10':
        header10 = DdsHeaderDxt10.load(file)
        fmt = header10.format

    size = header.spf.size * header.width * header.height // 8
    data = file.read(size)

    print(target, fmt, header.spf)
    if fmt == 87:  # B8G8R8A8
        img = np.array(tuple(data), dtype='uint8').reshape(
            (header.height, header.width, 4))
        cv.imwrite(target, img)
        return
    if fmt == 'DXT1':
        img = np.zeros((header.height, header.width, 3), dtype='uint8');
        do_bc1(img, data)
        cv.imwrite(target, img)
        return
    if fmt == 80: # BC4
        img = np.zeros((header.height, header.width), dtype='uint8');
        do_bc4(img, data)
        cv.imwrite(target, img)
        return
    print(target, fmt)
    #raise NotImplementedError(fmt)


#@click.command()
#@click.option('--output', '-o', default=None)
#@click.argument('filename')
def main(filename, output):
    if not output:
        output = filename + '.png'
    # if os.path.exists(output):
    #     #print(output)
    #     return
    with open(filename, 'rb') as file:
        extract(file, output)


for a in sys.argv[1:]:
    try:
        main(a, None)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        pass
