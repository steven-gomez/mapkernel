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

def get_isolated_tile(x, y, im, legend):
    # Check for backup in non-contextual tiles
    c = legend.get_class(im.getpixel((x,y)))
    material_name = legend.describe(c)

    tex_dir = os.path.join('data', 'tiles', material_name)
    files = []
    try:
        files = os.listdir(tex_dir)
    except:
        return None

    matching_tiles = list(filter(isPNG, files))
    if len(matching_tiles) == 0:
        #print('ERROR: No tiles at all for {},{}'.format(x,y))
        return None
    else:
        patch = os.path.join(tex_dir, random.choice(matching_tiles))
        return Image.open(patch)


def generate_full_map(downsampled_im, legend):
    im = downsampled_im
    (w,h) = im.size

    upsampled_im = Image.new(mode="RGBA", size=(w*16, h*16))

    # For each row, go through each column and decide what to composite
    i = 0
    for y in range(h):
        for x in range(w):
            ns = Neighbors.get_neighbors(x, y, im)

            # Get a tile Image
            # Try contextual first, then an isolated tile
            tile = get_contextual_tile(ns)
            if tile is None:
                tile = get_isolated_tile(x, y, im, legend)
            if tile:
                upsampled_im.paste(tile, (x*16,y*16))
                if i%32 == 0:
                    print(".", end ="", flush=True)
            else:
                print("x", end ="", flush=True)

            i += 1

    upsampled_im.save('test_out.png')
    print("Done")


def get_unique_texels(im):
    (w,h) = im.size
    uniques = {}
    for x in range(w):
        for y in range(h):
            new_tex = Neighbors.get_neighbors(x, y, im)
            #print(new_tex.code())
            if new_tex.code() in uniques:
                uniques[new_tex.code()] += 1
            else:
                uniques[new_tex.code()] = 1
    return uniques

class Neighbors:
    def __init__(self, nbs):
        self.nw = nbs[0]
        self.n = nbs[1]
        self.ne = nbs[2]
        self.w = nbs[3]
        self.c = nbs[4]
        self.e = nbs[5]
        self.sw = nbs[6]
        self.s = nbs[7]
        self.se = nbs[8]

    @staticmethod
    def get_neighbors(x, y, img):
        (w,h) = img.size
        neighbors_list = []

        for y_offset in [-1, 0, 1]:
            for x_offset in [-1, 0, 1]:
                px = 'None'
                try:
                    px = im.getpixel((x+x_offset,y+y_offset))
                except:
                    pass
                neighbors_list.append(px)

        return Neighbors(neighbors_list)

    def code(self):
        return 'context-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(
            str(self.nw),
            str(self.n),
            str(self.ne),
            str(self.w),
            str(self.c),
            str(self.e),
            str(self.sw),
            str(self.s),
            str(self.se)
        )

def args():
    """Sets up CLI args and returns a parsed args objects."""
    parser = argparse.ArgumentParser(description='Transform map')
    parser.add_argument('input_img', type=str, help='PNG map image filepath')
    parser.add_argument('--legend', action='store_true',  help='Generate legend interactively')
    return parser.parse_args()

if __name__ == "__main__":
    args = args()
    map_fp = args.input_img
    print(map_fp)
    print("Running mapping")

    # Open image file
    im = Image.open(map_fp)
    print(im.format, im.size, im.mode)
    #im.show()

    # Get a legend for this map
    legend = Legend()
    if args.legend:
        legend = Legend(im)
    else:
        print("Loading legend.json")
        legend = Legend.load('legend.json')

    unique_nbs = get_unique_texels(im)
    print("Got {} unique neighborhoods".format(len(unique_nbs)))


    import pprint as pp
    context_tiles_dir = 'data/tiles-contextual/'
    top_nbs = { tex:count for (tex,count) in unique_nbs.items() if count >= 10 }
    #pp.pprint(top_nbs)
    print("Found {} neighborhoods that appeared at least 10 times".format(len(top_nbs)))
    for k in top_nbs:
        pathlib.Path(context_tiles_dir+k).mkdir(parents=True, exist_ok=True)
    generate_full_map(im, legend)
