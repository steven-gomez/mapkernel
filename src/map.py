import sys, os, json, pathlib
import argparse
import random
from neighbors import Neighbors
from PIL import Image, ImageFilter
from legend import Legend
from tile import get_tile, isPNG

random.seed(10)


def composite(top_im, bottom_im):
    out = bottom_im.copy()
    out.paste(top_im, (0,0), top_im)
    return out

def generate_full_map(downsampled_layers_lst, legend, specials_dir=None):
    layers = []
    out = None
    i = 0

    # Get an upsampled layer for each of the layers
    for im in downsampled_layers_lst:
        print('')
        print("Layer {}".format(i))
        # Store each layer
        j = (i==0)
        new_layer = upsample(im, legend, base_layer=j)
        layers.append(new_layer)

        # Composite onto output img
        if out == None:
            out = new_layer.copy()
        else:
            out = composite(new_layer, out)

        i += 1

    composite_specials(out, specials_dir)

    out_fn = 'test_out.png'
    out.save(out_fn)
    print("Saved output to {}".format(out_fn))
    return out

def upsample(downsampled_layer_img, legend, base_layer=True):
    print("Base layer?", base_layer)
    im = downsampled_layer_img
    (w,h) = im.size

    upsampled_im = Image.new(mode="RGBA", size=(w*16, h*16))
    overlaps = None


    # For each row, go through each column and decide what to composite
    i = 0  # pixel index
    for y in range(h):
        for x in range(w):
            # Printout for debugging
            if i%32 == 0:
                print(".", end ="", flush=True)

            ns = Neighbors.get_neighbors(x, y, im)

            # Get a tile Image
            material, tile = get_tile(x, y, im, legend)

            # Put down a base layer of the tile
            pastes = 0
            if tile and base_layer:
                upsampled_im.paste(tile, (x*16,y*16))
                pastes += 1

            # Look for tiles to composite on top on this one
            diffs = ns.different()
            diffs.sort(key = lambda x: x[0])
            ol = None


            # If at a boundary
            if len(diffs) > 0:
                ol = get_overlap_patch(material, diffs, legend)
                if ol is None:
                    # No overlap tile, so use blocky plain tile
                    ol = tile

            # If interior use regular tile
            elif len(diffs) == 0:
                ol = tile

            # Paste the overlay if there is one. (Guaranteed in base layer, but
            # not higher layers if no material at a pixel.)
            if ol:
                upsampled_im.paste(ol, (x*16,y*16), ol)

            i += 1

    print('Done')
    upsampled_im.show()

    return upsampled_im

def get_overlap_patch(material, diffs, legend):
    patch_fn = ""
    is_first = True
    for nb in diffs:
        nb_material_class = legend.get_class(nb[1])
        if is_first:
            is_first = False
        else:
            patch_fn += '_'
        patch_fn += "{}-{}".format(nb[0], legend.describe(nb_material_class))
    patch_fn += '.png'

    ol_fp = os.path.join('data', 'tiles', 'overlaps', material, patch_fn)
    try:
        return Image.open(ol_fp)
    except:
        return None

def composite_specials(full_map, specials_dir):
    if specials_dir is None or full_map is None:
        return

    specials = list(filter(isPNG, os.listdir(specials_dir)))
    for s in specials:
        parts = s.split('_')
        # Split off the file extension, then get the comma-separated parts
        coords = list(map(int, parts[1].split('.')[0].split(',')))
        scaled_coords = list(map(lambda c: c*16, coords))
        print("Compositing '{}' at {} => upsampled {}".format(parts[0], coords, scaled_coords))
        patch = Image.open(os.path.join(specials_dir, s))
        full_map.paste(patch, scaled_coords, patch)


def args():
    """Sets up CLI args and returns a parsed args objects."""
    parser = argparse.ArgumentParser(description='Transform map')
    parser.add_argument('input_imgs', nargs='+', type=str, help='PNG map layer image filepaths')
    parser.add_argument('-l', '--legend', action='store_true',  help='Generate legend interactively')
    parser.add_argument('-s', '--specials_dir', nargs='?', default=None, help='Path to dir of special patchs to composite')
    return parser.parse_args()

if __name__ == "__main__":
    args = args()
    map_fp_lst = args.input_imgs
    print("Running mapping")

    # Open image files
    layers = []
    for map_fp in map_fp_lst:
        im = Image.open(map_fp)
        print(map_fp, im.format, im.size, im.mode)
        layers.append(im)
    #im.show()

    # Get a legend for this map
    legend = Legend()
    if args.legend:
        legend = Legend(layers)
    else:
        print("Loading legend.json")
        legend = Legend.load('legend.json')

    if args.specials_dir:
        if not os.path.isdir(args.specials_dir):
            print("Cannot open directory of special composites: {}".format(args.specials_dir))
            print("Skipping special composites")
        else:
            print("Using specials directory '{}'".format(args.specials_dir))
    else:
        print("Skipping special composites")


    """
    unique_nbs = get_unique_texels(im)
    print("Got {} unique neighborhoods".format(len(unique_nbs)))


    import pprint as pp
    context_tiles_dir = 'data/tiles-contextual/'
    top_nbs = { tex:count for (tex,count) in unique_nbs.items() if count >= 10 }
    #pp.pprint(top_nbs)
    print("Found {} neighborhoods that appeared at least 10 times".format(len(top_nbs)))
    for k in top_nbs:
        pathlib.Path(context_tiles_dir+k).mkdir(parents=True, exist_ok=True)
    """

    generate_full_map(layers, legend, specials_dir=args.specials_dir)
