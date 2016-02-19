import numpy as np
import matplotlib as mpl
import matplotlib.pylab as pl
from matplotlib.gridspec import GridSpec

class InteractiveInput(object):
    def __init__(self, im, new_cmap='bone', figsize=8):
        self.new_cmap = new_cmap
        self.im = im
        self.figsize = figsize

        self.imargs = {'interpolation': 'none'}
        self.modes = ['original', 'preview']
        self.mode = self.modes[0]

        sh = im.shape[:2]
        q = float(sh[1]) / float(sh[0])

        self.fig = pl.figure(figsize=(self.figsize*q,self.figsize))
        self.ax = self.fig.add_axes([0, 0, 1, 1])

        self.draw()
        self.register_events()

    def _format_ax(self, ax):
        ax.set_xticks([])
        ax.set_yticks([])

    def draw(self):
        self.ax.imshow(self.im, **self.imargs)
        self._format_ax(self.ax)

    def register_events(self):
        self._calls = []

        self._calls.append(self.fig.canvas.mpl_connect('key_press_event', self.key_press_event))

        if self.mode == 'original':
            self._calls.append(self.fig.canvas.mpl_connect('button_press_event', self.mouse_press_view))
        if self.mode == 'preview':
            self._calls.append(self.fig.canvas.mpl_connect('button_press_event', self.mouse_press_add))

    def _pt_xy(self, event):
        x0 = event.xdata
        y0 = event.ydata
        return np.array([x0, y0])

    def mouse_press_view(self, event):
        self.event = event
        p = self._pt_xy(event)

        if p is not None:
            print "Moving view to %r" % p
            self.slices = p
        self.draw()

    def mouse_press_add(self, event):
        self.event = event

        p = self._pt_xyz(event)
        if p is not None:
            p = np.array(p)
            r = self.state.obj.rad[self.state.obj.typ==1.].mean()

            print "Adding particle at", p, r
            self.state.add_particle(p, r)
        self.set_field()
        self.draw()

    def mouse_press_remove(self, event):
        self.event = event

        p = self._pt_xyz(event)
        if p is not None:
            print "Removing particle near", p
            self.state.remove_closest_particle(p)
        self.set_field()
        self.draw()

    def mouse_press_optimize(self, event):
        self.event = event
        p = self._pt_xyz(event)

        if p is not None:
            print "Optimizing particle near", p
            n = self.state.closest_particle(p)
            bl = self.state.blocks_particle(n)
            runner.sample_state(self.state, bl, stepout=0.1, doprint=True, N=3)

        self.set_field()
        self.draw()

    def key_press_event(self, event):
        self.event = event

        if event.key == 'q':
            self.mode = 'original'
        if event.key == 'w':
            self.mode = 'preview'

        print "Switching mode to", self.mode

        for c in self._calls:
            self.fig.canvas.mpl_disconnect(c)

        self.register_events()
