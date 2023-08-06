from pylab import *
from rpy2.robjects import r as rcode


__all__ = ["RColorMap"]


class RColorMap(object):

    def __init__(self, name, inverse=True, N=10):

        self._name = name
        self.rN = 1000   # number of colors to retrieve from R colors
        self.n = 11     # number of colors to really use
        self.N = N      # number of colors in the colorbar
        self.inverse = inverse
        self._xvalues = None
        self._colors = None

    def _get_name(self):
        return self._name
    name = property(_get_name)

    def _get_x(self):
        return linspace(0, self.rN-1, self.n)
    xvalues = property(_get_x)

    def _get_rgb(self):
        if self._colors == None:
            self._colors = self._getRGBColors()
        return self._colors
    rgb = property(_get_rgb)

    def _get_r(self):
        return [x[0:2] for x in self.rgb]
    r = property(_get_r)
    def _get_g(self):
        return [x[2:4] for x in self.rgb]
    g = property(_get_g)
    def _get_b(self):
        return [x[4:6] for x in self.rgb]
    b = property(_get_b)

    def _getRGBColors(self):
         
        params = {'N':self.rN, 'n':self.n, 'name':self.name} 
        code = """
        colors = %(name)s.colors(%(N)s)
        r = c(seq(from=1,to=%(N)s, length.out=%(n)s))
        colors[r]
        """ % params
        try:
            res = rcode(code) 
        except:
            print("Could not find the %s color" % self.name)

        # colors returned by R stqrts with # character and all ends with FF
        # All we need is the 6 characters corresponding to the RGB color coded with hexadecimal 
        res = [x[1:7] for x in res]   
        if self.inverse:
            res = res[::-1]
        return res
     
    def hex2dec(self, data):
        return int(data,16)*1.0/255


    def colormap(self, N=256):
        rcol = []
        bcol = []
        gcol = []
        for x, r, g, b in zip(self.xvalues, self.r, self.g, self.b):
            rcol.append((x/float(self.rN-1), self.hex2dec(r), self.hex2dec(r)))
            gcol.append((x/float(self.rN-1), self.hex2dec(g), self.hex2dec(g)))
            bcol.append((x/float(self.rN-1), self.hex2dec(b), self.hex2dec(b)))
        rcol = tuple(rcol)
        bcol = tuple(bcol)
        gcol = tuple(gcol)

        colors = {'red':rcol, 'green':gcol, 'blue':bcol}
        #print colors
        f = matplotlib.colors.LinearSegmentedColormap
        m = f('my_color_map', colors, N)
        return m


