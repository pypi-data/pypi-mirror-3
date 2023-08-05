from ..core import Object
from .core import Plottable
from .hist import HistStack
import ROOT


class Legend(Object, ROOT.TLegend):

    def __init__(self, nentries,
                       pad=None,
                       leftmargin=0.,
                       bottommargin=0):
        buffer = 0.03
        height = 0.06 * nentries + buffer
        if pad is None:
            pad = ROOT.gPad
        ROOT.TLegend.__init__(self, pad.GetLeftMargin() + buffer + leftmargin,
                                    (1. - pad.GetTopMargin()) - height,
                                    1. - pad.GetRightMargin(),
                                    ((1. - pad.GetTopMargin()) - buffer))
        self.pad = pad
        self.UseCurrentStyle()
        self.SetEntrySeparation(0.2)
        self.SetMargin(0.1)
        self.SetFillStyle(0)
        self.SetFillColor(0)
        self.SetTextFont(ROOT.gStyle.GetTextFont())
        self.SetTextSize(ROOT.gStyle.GetTextSize())

    def Height(self):

        return abs(self.GetY2() - self.GetY1())

    def Width(self):

        return abs(self.GetX2() - self.GetX1())

    def Draw(self, *args, **kwargs):

        ROOT.TLegend.Draw(self, *args, **kwargs)
        self.UseCurrentStyle()
        self.pad.Modified()
        self.pad.Update()

    def AddEntry(self, thing, legendstyle=None):

        if isinstance(thing, HistStack):
            things = thing
        elif isinstance(thing, Plottable):
            things = [thing]
        else:
            raise TypeError("Can't add object of type %s to legend" % \
                            type(thing))
        for hist in things:
            if hist.inlegend:
                if legendstyle is None:
                    legendstyle = hist.legendstyle
                ROOT.TLegend.AddEntry(self, hist, hist.GetTitle(), legendstyle)
        self.pad.Modified()
        self.pad.Update()
