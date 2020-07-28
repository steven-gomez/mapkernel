import json

class Legend:
    def get_class(self, p):
        """Decodes a pixel values into a class label.
        """
        cls = 'UNKNOWN_CLASS'
        if str(p) in self.classes:
            cls = self.classes[str(p)]
        return cls

    def describe(self, c):
        """Returns a human-readable label of an input class using the legend.""" 
        desc = 'UNKNOWN_DESC'
        if str(c) in self.desc:
            desc = self.desc[str(c)]
        return desc

    def __init__(self, im=None):
        self.classes = {}
        self.desc = {}
        if im:
            uniques = Legend.get_unique_pixels(im)
            class_ind = 0
            for p in uniques:
                single_im = Image.new(mode="RGBA", size=(100, 100), color=p)
                single_im.show()
                print("What does this color class represent in the map?:")
                desc = input()
                k = str(p)
                self.classes[k] = str(class_ind)
                self.desc[class_ind] = desc
                class_ind += 1
            self.write()

    @staticmethod
    def load(legend_json_fp='legend.json'):
        """Loads a Legend object from a saved JSON file and returns it.

        Args:
        legend_json_fp (str): file path for the JSON file.
            Looks for 'legend.json' in current directory if None.
        """
        print("Loading {}...".format(legend_json_fp))
        with open(legend_json_fp, 'r') as f:
            loaded = json.loads(f.read())
            new_leg = Legend()
            new_leg.classes = loaded['classes']
            new_leg.desc = loaded['desc']
            print("Loaded")
            return new_leg

    def write(self, out_fp='legend.json'):
        """Writes the legend to a JSON file.

        Args:
        out_fp (str): optional file path for the output file.
        """

        print("Writing {}...".format(out_fp))
        with open(out_fp, 'w') as file:
            file.write(json.dumps(vars(self)))

    @staticmethod
    def get_unique_pixels(im):
        """Returns a dict of all pixel tuples (k) and their counts (v)."""
        uniques = {}
        for p in im.getdata():
            if p in uniques:
                uniques[p] += 1
            else:
                uniques[p] = 1
        return uniques
