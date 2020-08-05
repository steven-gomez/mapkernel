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
                px = (0,0,0,0)
                try:
                    px = img.getpixel((x+x_offset,y+y_offset))
                except:
                    pass
                neighbors_list.append(px)

        return Neighbors(neighbors_list)

    def different(self):
        res = []

        if self.n != self.c:
            res.append(('n', self.n))
        if self.e != self.c:
            res.append(('e', self.e))
        if self.w != self.c:
            res.append(('w', self.w))
        if self.s != self.c:
            res.append(('s', self.s))
        return res

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
