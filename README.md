# Control Game File Unpacker

Extractors / converters for various Control / Northlight file formats.

My main goals are:
- understanding level geometry data, and how northlight works in general
- creating a tool to edit level data / geometry
- creating a repack tool, and hopefuly running the game with new level data.

Other goals are:
- creating converter to and from all compiled formats
- creating editors for those formats

Feel free to send a PR, if you implemented anything else.

Currently implemented:

- rmdp.py: extractor for game package files
- rmdl.py: extractor for level files (found in `/data/worlds/...`)
- texco.py: converter for textures (from DDS to PNG)
- strings.py: extractor for `string_table.bin` file.

In implementation:

- umbratile.py: extractor for umbratile files from levels (level geometry?)

Read more about the file formats documented in [file_formats.md](file_formats.md).

## Prerequisites

You'll need following python packages. `opencv` is only required for texture converter.
```
click
opencv
```

## Running

Most extractors take just the path to the file you want to extract and output (`-o` / `--output`) path. Output is either a file, or directory for packages (which will be created).

`rmdp` takes the filename without extension, and then opens all three files (which should be called the same with different extensions).

E.g.
```
python rmdp.py /path/to/ep100-000-generic -o result
```
will create a directory `result` in which data from the given archive will be extracted.