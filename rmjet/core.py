import PIL
import numpy as np

from matplotlib import cm

def safe_cmap(cmap):
    """
    Convert a cmap into a good cmap, either from a string or check whether
    it is indeed a function
    """
    if isinstance(cmap, basestring):
        cmap = cm.__dict__.get(cmap, None)

        # make sure we have a colormap
        if cmap is None:
            raise AttributeError("No such colormap found in matplotlib, %s" % cmap)

    if not hasattr(cmap, '__call__'):
        raise AttributeError("cmap `%s` is not callable" % cmap)
    return cmap

class InvertedColorMap(object):
    def __init__(self, cmap='jet', vrange=(0,1), xtol=1.0/255):
        """
        Numerically inverts a colormap so that you can request the values that
        produces a certain color. Since it is numerical there is a tolerance
        value that you may specify with xtol.

        Parameters:
        -----------
        cmap : function, string
            The forward colormap you would like to invert. Either is a function
            that returns a color for a ndarray of values 0 -> 1 or a name of
            one of the matplotlib colormaps.

        vrange : list-like
            The vmin and vmax of the values returned by the inversion.

        xtol : float
            Numerical tolerance of inverted values.
        """
        self.xtol = xtol
        self.cmap = safe_cmap(cmap)
        self.vrange = vrange

        self.x = np.linspace(0.0, 1.0, 1.0/self.xtol)
        self.y = self.cmap(self.x)

    def colors(self, x):
        """ Returns color given some values """
        return self.cmap(x)

    def values(self, c):
        """ Computes the values corresponding to a set of colors. """
        if not isinstance(c, np.ndarray):
            c = np.array(c)

        if len(c.shape) == 2:
            c = c[:,None,:]
        elif len(c.shape) == 3:
            c = c[:,:,None,:]

        # get the difference between colors and possible colors.
        # from there, get the associated values
        # FIXME -- do linear interpolation to values when possible?
        diff = np.sqrt(((c - self.y)**2).sum(axis=-1))
        inds = diff.argmin(axis=-1)
        vals = norm(self.x[inds], vrange=self.vrange)

        # get the errors for these values and use that to make a masked array
        diff = diff.min(axis=-1)
        masked = np.ma.masked_array(vals, mask=diff > 10*self.xtol)
        return masked

def norm(d, vrange=(0.0, 1.0)):
    vmin, vmax = vrange
    return (vmax - vmin)*(d - d.min()) / d.ptp() - vmin

def read_image(filename):
    """
    Read any image PIL can read and return as numpy array.  Simple wrapper to
    PIL in case complexity is added, though I can't think of what that might be
    """
    return norm(np.asarray(PIL.Image.open(filename)))

def write_image(data, filename):
    """
    Write the image to the appropriate image file, type given by extension
    """
    im = PIL.Image.fromarray(data.astype("uint8"))
    im.save(filename)

def convert_color(data, cmaps=('jet', 'bone'), vrange=(0,1)):
    """
    Convert the image `data` to a new colormap given by the colormap set
    `cmaps`. If the data extends around 0 (so there is positive and negative
    data) it is often advantageous to use a diverging colormap centered about
    0. In this case, the range of the data can be provided to properly center
    the colormap.

    Parameters:
    -----------
    data : ndarray, shape [M,N,{3,4}]
        Image data which contains color channels (either 3 or 4 with alpha).

    cmaps : tuple
        The colormaps to use, input and output. Can either be a string or a
        colormap object such as those provided in `mpl.cm` of type
        `matplotlib.colors.LinearSegmentedColormap`.

    vrange : tuple
        The value range of the data in the image. This parameter is only
        relevant if the data contains zero and a diverging colormap is desired,
        otherwise leave as default.

    Returns:
    --------
    values : masked array
        A masked ndarray of the actual values determined by the colormap
        inference routine.

    output : ndarray, shape [M,N,{3,4}]
        Resulting image after the colormap transformation.
    """
    cmaps = [safe_cmap(i) for i in cmaps]
    inv = InvertedColorMap(cmaps[0], vrange=vrange)
    val = inv.values(data)

    out = data.copy()
    out[~val.mask] = cmaps[1](val.data[~val.mask])
    return out
