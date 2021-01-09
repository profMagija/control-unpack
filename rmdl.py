import struct
import sys
import click
import os

def _read(file, fmt, size=None):
    if size is None:
        size = struct.calcsize(fmt)
    return struct.unpack(fmt, file.read(size))
    
def _readLpString(file, lformat='i'):
    length = _read(file, lformat)[0]
    return file.read(length).decode()

def extract(file, filename):
    magic = file.read(4)
    if magic != b'RMDL':
        print('invalid file')
        return
    
    directory_length = _read(file, 'i')[0]
    file.seek(-directory_length, 2)
    
    count_files = _read(file, 'i')[0]
    
    parts = []
    for _ in range(count_files):
        parts.append((_read(file, 'i')[0], _readLpString(file)))
    
    dirname = os.path.splitext(filename)[0]
    # print(dirname)
    os.makedirs(dirname, exist_ok=True)
    
    file.seek(8)
    
    for part_length, part_name in parts:
        # print(os.path.join(dirname, part_name))
        with open(os.path.join(dirname, part_name), 'wb') as part_file:
            part_file.write(file.read(part_length))

# @click.command()
# @click.argument('filename')
def main(filename):
    print(filename)
    with open(filename, 'rb') as file:
        extract(file, filename)

for filename in sys.argv:
    main(filename)