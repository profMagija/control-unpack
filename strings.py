import click
import io
import struct
import array
import os
import json


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


# IMGS = {
#     'opcon_doc_hissresearch_01_DESCRIPTION1': 'floater',
#     'opcon_doc_hissresearch_02_DESCRIPTION1': 'guard',
#     'opcon_doc_hissresearch_03_DESCRIPTION1': 'ranger_t1',
#     'opcon_doc_hissresearch_04_DESCRIPTION1': 'enraged',
#     'opcon_doc_hissresearch_05_DESCRIPTION1': 'knight',
#     'opcon_doc_hissresearch_06_DESCRIPTION1': 'sniper',
#     'opcon_doc_hissresearch_07_DESCRIPTION1': 'drifter',
#     'opcon_doc_hissresearch_08_DESCRIPTION1': 'tempest',
#     'opcon_doc_hissresearch_09_DESCRIPTION1': 'master',
#     'opcon_doc_hissresearch_10_DESCRIPTION1': 'hiss_cluster',
#     'opcon_doc_hissresearch_12_DESCRIPTION1': 'demoman',
#     'opcon_doc_ai_anchor_01_DESCRIPTION1': 'opcon_ai_anchor',
#     'opcon_doc_ai_balloon_01_DESCRIPTION1': 'opcon_ai_balloon',
#     'opcon_doc_ai_duck_01_DESCRIPTION1': 'opcon_ai_duck',
#     'opcon_doc_ai_fan_01_DESCRIPTION1': 'opcon_ai_fan',
#     'opcon_doc_ai_flamingo_01_DESCRIPTION1': 'opcon_ai_flamingo',
#     'opcon_doc_ai_fridge_01_DESCRIPTION1': 'opcon_ai_fridge',
#     'opcon_doc_ai_globe_01_DESCRIPTION1': 'opcon_ai_globe',
#     'opcon_doc_ai_hand_01_DESCRIPTION1': 'opcon_ai_hand',
#     'opcon_doc_ai_jukebox_01_DESCRIPTION1': 'opcon_ai_jukebox',
#     'opcon_doc_ai_lantern_01_DESCRIPTION1': 'opcon_ai_lantern',
#     'opcon_doc_ai_letter_01_DESCRIPTION1': 'opcon_ai_letter',
#     'opcon_doc_ai_mailbox_01_DESCRIPTION1': 'opcon_ai_mailbox',
#     'opcon_doc_ai_mannequin_01_DESCRIPTION1': 'opcon_ai_mannequin',
#     'opcon_doc_ai_manuscript_01_DESCRIPTION1': 'opcon_ai_manuscript_page',
#     'opcon_doc_ai_mirror_01_DESCRIPTION1': 'opcon_ai_mirror',
#     'opcon_doc_ai_basket_01_DESCRIPTION1': 'opcon_ai_picnic_basket',
#     'opcon_doc_ai_pram_01_DESCRIPTION1': 'opcon_ai_pram',
#     'opcon_doc_ai_roulette_01_DESCRIPTION1': 'opcon_ai_roulette',
#     'opcon_doc_ai_sledgehammer_01_DESCRIPTION1': 'opcon_ai_sledgehammer',
#     'opcon_doc_ai_surfboard_01_DESCRIPTION1': 'opcon_ai_surfboard',
#     'opcon_doc_ai_swanboat_01_DESCRIPTION1': 'opcon_ai_swan_boat',
#     'opcon_doc_ai_thermos_01_DESCRIPTION1': 'opcon_ai_thermos',
#     'opcon_doc_ai_trafficlight_01_DESCRIPTION1': 'opcon_ai_traffic_light',
#     'opcon_doc_ai_tree_01_DESCRIPTION1': 'opcon_ai_tree',
#     'opcon_doc_ai_watercooler_01_DESCRIPTION1': 'opcon_ai_water_cooler',
#     'opcon_doc_oop_ashtray_01_DESCRIPTION1': 'opcon_oop_ashtray',
#     'opcon_doc_oop_carouselhorse_01_DESCRIPTION1': 'opcon_oop_carousel_horse',
#     'opcon_doc_oop_disk_01_DESCRIPTION1': 'opcon_oop_disk',
#     'opcon_doc_oop_projector_01_DESCRIPTION1': 'opcon_oop_projector',
#     'opcon_doc_oop_safe_01_DESCRIPTION1': 'opcon_oop_safe',
#     'opcon_doc_oop_serviceweapon_01_DESCRIPTION1': 'opcon_oop_service_weapon',
#     'opcon_doc_oop_telephone_01_DESCRIPTION1': 'opcon_oop_telephone',
#     'opcon_doc_oop_television_01_DESCRIPTION1': 'opcon_oop_television',
#     'opcon_doc_oop_xray_01_DESCRIPTION1': 'opcon_oop_xray',
# }

RES = {}

def extract(file: io.BufferedIOBase, target: io.TextIOBase):
    mn = file.read(2)

    if mn == b'\x95\x30':
        file.read(2)
    else:
        raise NotImplementedError(mn)

    while True:
        keylenb = file.read(4)
        if not keylenb:
            break
        keylen = struct.unpack('I', keylenb)[0]
        key = file.read(keylen).decode('ascii')
        vallen = struct.unpack('I', file.read(4))[0]
        val = file.read(vallen * 2).decode('utf-16le')
        # print(key, val)
        RES[key] = val
        # if key.startswith('opcon_doc_') and key.endswith('DESCRIPTION1'):
        #     if key in IMGS:
        #         target.write(
        #             f'<img src="./result/data_pc/uiresources/p7/images/4k/images/narrative/{IMGS[key]}.tex.png">\n')
        #         IMGS.pop(key)
        #     target.write(val)
        #     target.write('<div class="page-break"></div>')
    
    json.dump(RES, target, indent=4)


@click.command()
@click.option('--output', '-o', default=None)
@click.argument('filename')
def main(filename, output):
    if not output:
        output = filename + '.txt'
    with open(filename, 'rb') as file:
        with open(output, 'w') as target:
#             target.write('''<html>
# <head>
# <link rel="stylesheet" href="./style.css">
# </head>
# <body>''')
            extract(file, target)
            # target.write('''</body></html>''')
    
    # print(IMGS.keys())


main()
