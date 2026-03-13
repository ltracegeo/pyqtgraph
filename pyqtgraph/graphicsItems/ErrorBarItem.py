import numpy as np
from .. import functions as fn
from .. import getConfigOption
from ..Qt import QtGui
from .GraphicsObject import GraphicsObject

__all__ = ['ErrorBarItem']

class ErrorBarItem(GraphicsObject):
    def __init__(self, **opts):
        """
        All keyword arguments are passed to setData().
        """
        GraphicsObject.__init__(self)
        self.opts = dict(
            x=None,
            y=None,
            height=None,
            width=None,
            top=None,
            bottom=None,
            left=None,
            right=None,
            beam=None,
            pen=None
        )
        self.setVisible(False)
        self.setData(**opts)

    def setData(self, **opts):
        self.opts.update(opts)
        self.setVisible(all(self.opts[ax] is not None for ax in ['x', 'y']))
        self.prepareGeometryChange()
        self.drawPath()
        self.update()
        self.informViewBoundsChanged()
        
    def setOpts(self, **opts):
        # for backward compatibility
        self.setData(**opts)
        
    def drawPath(self):
        p = QtGui.QPainterPath()
        
        x, y = self.opts['x'], self.opts['y']
        if x is None or y is None:
            self.path = p
            return
        
        beam = self.opts['beam']
        
        height, top, bottom = self.opts['height'], self.opts['top'], self.opts['bottom']
        if height is not None or top is not None or bottom is not None:
            ## draw vertical error bars
            if height is not None:
                y1 = y - height/2.
                y2 = y + height/2.
            else:
                if bottom is None:
                    y1 = y
                else:
                    y1 = y - bottom
                if top is None:
                    y2 = y
                else:
                    y2 = y + top

            xs = fn.interweaveArrays(x, x)
            y1_y2 = fn.interweaveArrays(y1, y2)
            verticalLines = fn.arrayToQPath(xs, y1_y2, connect="pairs")
            p.addPath(verticalLines)

            if beam is not None and beam > 0:
                x1 = x - beam/2.
                x2 = x + beam/2.

                x1_x2 = fn.interweaveArrays(x1, x2)
                if height is not None or top is not None:
                    y2s = fn.interweaveArrays(x1_x2, x1_x2) # wait, this was wrong in original? No, xs was x,x.
                    # Wait, looking at original code:
                    # x1_x2 = fn.interweaveArrays(x1, x2)
                    # if height is not None or top is not None:
                    #     y2s = fn.interweaveArrays(y2, y2)
                    #     topEnds = fn.arrayToQPath(x1_x2, y2s, connect="pairs")
                    #     p.addPath(topEnds)
                    y2s = fn.interweaveArrays(y2, y2)
                    topEnds = fn.arrayToQPath(x1_x2, y2s, connect="pairs")
                    p.addPath(topEnds)

                if height is not None or bottom is not None:
                    y1s = fn.interweaveArrays(y1, y1)
                    bottomEnds = fn.arrayToQPath(x1_x2, y1s, connect="pairs")
                    p.addPath(bottomEnds)

        width, right, left = self.opts['width'], self.opts['right'], self.opts['left']
        if width is not None or right is not None or left is not None:
            ## draw vertical error bars
            if width is not None:
                x1 = x - width/2.
                x2 = x + width/2.
            else:
                if left is None:
                    x1 = x
                else:
                    x1 = x - left
                if right is None:
                    x2 = x
                else:
                    x2 = x + right
            
            ys = fn.interweaveArrays(y, y)
            x1_x2 = fn.interweaveArrays(x1, x2)
            ends = fn.arrayToQPath(x1_x2, ys, connect='pairs')
            p.addPath(ends)

            if beam is not None and beam > 0:
                y1 = y - beam/2.
                y2 = y + beam/2.
                y1_y2 = fn.interweaveArrays(y1, y2)
                if width is not None or right is not None:
                    x2s = fn.interweaveArrays(x2, x2)
                    rightEnds = fn.arrayToQPath(x2s, y1_y2, connect="pairs")
                    p.addPath(rightEnds)

                if width is not None or left is not None:
                    x1s = fn.interweaveArrays(x1, x1)
                    leftEnds = fn.arrayToQPath(x1s, y1_y2, connect="pairs")
                    p.addPath(leftEnds)
                    
        self.path = p
        
        
    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        if self.opts['x'] is None or self.opts['y'] is None:
            return None
        
        x = self.opts['x']
        y = self.opts['y']
        
        if ax == 0:
            d = x
            if self.opts['width'] is not None:
                w = self.opts['width']
                return (np.min(d - w/2.), np.max(d + w/2.))
            elif self.opts['left'] is not None or self.opts['right'] is not None:
                l = self.opts['left'] if self.opts['left'] is not None else 0
                r = self.opts['right'] if self.opts['right'] is not None else 0
                return (np.min(d - l), np.max(d + r))
            else:
                return (np.min(d), np.max(d))
        else:
            d = y
            if self.opts['height'] is not None:
                h = self.opts['height']
                return (np.min(d - h/2.), np.max(d + h/2.))
            elif self.opts['bottom'] is not None or self.opts['top'] is not None:
                b = self.opts['bottom'] if self.opts['bottom'] is not None else 0
                t = self.opts['top'] if self.opts['top'] is not None else 0
                return (np.min(d - b), np.max(d + t))
            else:
                return (np.min(d), np.max(d))

    def paint(self, p, *args):
        if self.path is None:
            self.drawPath()
        pen = self.opts['pen']
        if pen is None:
            pen = getConfigOption('foreground')
        p.setPen(fn.mkPen(pen))
        p.drawPath(self.path)
            
    def boundingRect(self):
        if self.path is None:
            self.drawPath()
        return self.path.boundingRect()
    
        
