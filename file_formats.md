# File format overview

## Random parts

### `0xD34DB33F` fragments

There are a number of fragments starting with a hex sequence `3F B3 4D D3` which when byteswapped reads `0xD34DB33F`. I think this is some sort of serialization format for game structures. The structure looks somewhat like this:

```c
struct deadbeef_object {
    uint32_t magic; // == 0xd34db33f
    uint32_t unknown_0; // version ??
    uint32_t length; // total length, including prev fields
    char data[length - 12];
};
```

## RMDP

A package of files, consists of three files (with extensions `.bin`, `.rmdp` and `.packmeta`). .bin file contains the directory structure and metadata, .rmdp contains the actual data all concatenated, and .packmeta contains some metadata (?) about some of the files.

### `.bin` structure

Everything is little endian.

```c
char zero;
uint32_t unknown_0; // i'm guessing version
uint32_t num_dirs;
uint32_t num_files;

char unknown_1[0x90]; // a bunch of data, not sure

struct dir_info {
    int64_t unknown_0; // similar to an index, but sometimes -1 and not completely sorted
    int64_t parent_index;
    int32_t unknown_1; // always zero ?
    int64_t dirname_offset; // offset of directory name
    int32_t unknown_2; // always zero ?
    int64_t unknown_3;
    int64_t unknown_4;
} dirs[num_dirs];

struct file_info {
    int64_t unknown_0; // similar to an index, but sometimes -1 and not completely sorted
    int64_t parent_index; // index of parent directory
    int32_t unknown_1; // always zero ?
    int64_t filename_offset; // offset of directory name
    int32_t unknown_2; // always zero ?
    int64_t content_offset;
    int64_t content_length;
} files[num_files];

char unknown_2[44]; //mostly 0xff, with 4 random characters in there

char names[...];
```

- `parent_index` is index into `dirs` array. Root directory has -1.
- `dirname_offset` and `filename_offset` are offsets into `names` array.
- `content_offset` and `content_length` are offset/length into `.rmdp` file.

## RMDL

A level (?) file, still is a ball of files.

Extracting it goes like this:

- read the magic number (4 bytes) == `RMDL`
- read the directory length (4 byte integer) `dirlen`
- go to `dirlen` bytes from the end of the file. directory structure:
  ```c
  struct rmdl_directory {
      uint32_t count;
      struct {
          uint32_t part_length;
          LpString part_name;
      } parts[count];
  }
  ```
- read the parts consecutively starting from 8th byte of the file (after the magic and dirlen)
- todo: understand the sturcture of each file in there

## Textures

The textures are in DirectDraw Surface format. Docs [here](https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide?redirectedfrom=MSDN).