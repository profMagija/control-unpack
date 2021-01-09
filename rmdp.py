import click
import io
import struct
import array
import os

def _read(file, fmt, size=None):
    if size is None:
        size = struct.calcsize(fmt)
    return struct.unpack(fmt, file.read(size))

def _filesize(f: io.BufferedIOBase): 
    pos = f.tell()
    f.seek(0, io.SEEK_END)
    result = f.tell()
    f.seek(pos)
    return result

def _skip(f, count):
    f.seek(count, os.SEEK_CUR)

def copy_data(source, offset, length):
    source.seek(offset)
    return source.read(length)

def read_text(a, b):
    a.seek(b)
    r = b''
    while (c := a.read(1)) != b'\0':
        r += c
    return r.decode('utf8')

def extract(meta: io.BufferedIOBase, binFile: io.BufferedIOBase, rmdp: io.BufferedIOBase, filter, target):
    pc_bin = 0
    fmt = '>'
    array = binFile.read(1);
    if array[0] == 0:
        pc_bin = 1
        fmt = '<'
    file_version, num_dirs, num_files = struct.unpack(fmt + 'iii', binFile.read(4 * 3))

    binFile.seek(0x9D)

    dirs = []
    full_names = []
    for i in range(num_dirs):
        _, parent, _, dirname, _, _, _ = _read(binFile, fmt + 'qqiqiqq')
        dirs.append((parent, dirname))

    r = []
    for i in range(num_files):
        _, dir_index, _, filename_offset, content_offset, content_length = _read(binFile, fmt+'qqiqqq')
        _skip(binFile, 16)

        r.append((filename_offset, content_offset, content_length, dir_index))

    _skip(binFile, 44)

    data_start = binFile.tell()

    for parent, dirname_offset in dirs:
        if dirname_offset == -1:
            full_names.append(target)
        else:
            dirname = read_text(binFile, data_start + dirname_offset)
            parent = full_names[parent]
            full_names.append(os.path.join(parent, dirname))

    for i, (filename_offset, content_offset, content_length, dir_index) in enumerate(r):
        filename = read_text(binFile, data_start + filename_offset)
        print(i, '/', len(r), end='\r')
        dirname = full_names[dir_index]
        os.makedirs(dirname, exist_ok=True)
        full_name = os.path.join(dirname, filename)
        with open(full_name, 'wb') as outf:
            outf.write(copy_data(rmdp, content_offset, content_length))

        
@click.command()
@click.option('--filter', '-f', default='')
@click.option('--output', '-o', default='.')
@click.argument('filename')
def main(filename, filter, output):
    with open(filename + '.packmeta', 'rb') as packmeta:
        with open(filename + '.bin', 'rb') as bin:
            with open(filename + '.rmdp', 'rb') as rmdp:
                extract(packmeta, bin, rmdp, filter, output)

main()
