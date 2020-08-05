import sys, os, json, pathlib
import argparse
import random
from PIL import Image, ImageFilter
from legend import Legend

random.seed(10)

def isPNG(fp):
    return fp.endswith('.png') or fp.endswith('.PNG')

def get_contextual_tile(ns):
    # Look for a contextual tile
    context_dir = os.path.join('data', 'tiles-contextual', ns.code())
    context_tiles = []
    try:
        context_tiles = os.listdir(context_dir)
    except:
        #print("WARN: No directory for context matching {}".format(ns.code()))
        return None

    context_tiles = list(filter(isPNG, context_tiles))
    if len(context_tiles) == 0:
        return None
    else:
        patch = os.path.join(context_dir, random.choice(context_tiles))
        return Image.open(patch)

def get_tile(x, y, im, legend):
    # Check for backup in non-contextual tiles
    c = legend.get_class(im.getpixel((x,y)))
    material_name = legend.describe(c)

    tex_dir = os.path.join('data', 'tiles', material_name)
    files = []
    try:
        files = os.listdir(tex_dir)
    except:
        #print("Got exception listing tiles for", material_name)
        return legend.describe(-1), None

    matching_tiles = list(filter(isPNG, files))
    if len(matching_tiles) == 0:
        #print('ERROR: No tiles at all for {},{}'.format(x,y))
        return None, None
    else:
        patch = os.path.join(tex_dir, random.choice(matching_tiles))
        return material_name, Image.open(patch)
