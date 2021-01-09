from construct import *
from hexdump import hexdump
import sys


def try_file(filename, parser):
    with open(filename, 'rb') as f:
        result = Struct(
            "thing" / parser,
            "rest" / GreedyBytes
        ).parse_stream(f)
        print(result['thing'])
        hexdump(result['rest'][:64])
    
        # print('left:', len(result['rest']) / f.tell() * 100)

def LpArray(item, ltype=Int32ul):
    return FocusedSeq(
        "data",
        "length" / ltype,
        "data" / Array(this.length, item)
    )
        
umbratile = Struct(
    Const(9, Int32ul),
    Const(1, Int32ul),
    Const("default", PascalString(Int32ul, 'utf8')),
    "edit_time" / Int32ul,
    LpArray(Const(0, Int32ul)),
    Const(0x408000003e800000, Int64ul),
    Const(0, Int32ul),
    "length_of_rest" / Int32ul,
    Const(0xd6000014, Int32ul),
    "what" / Hex(Int32ul),
    "length_again" / Int32ul,
    # "some_array" / Int16ul[32]
    # Const(b'p\x04\x00\x00\x00\x00\x80A\x00\x00\x00\x00\x00\x00', Bytes()\xd0D\x00\x00\x80\xc3\x00\x00', Bytes(22))
)

files = sys.argv[1:]

import random
random.shuffle(files)

for file in files[:20]:
    print(file)
    try_file(file, umbratile)