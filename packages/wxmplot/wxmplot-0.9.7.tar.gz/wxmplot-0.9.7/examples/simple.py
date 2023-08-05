#!/usr/bin/python
#
# simple example of MPlot

import wx
import numpy
import wxmplot

x   = numpy.arange(0.0,10.0,0.1)
y   = numpy.sin(2*x)/(x+2)
app = wx.PySimpleApp()

pframe = wxmplot.PlotFrame()
pframe.plot(x, y, title='Test Plot',
            xlabel=r'  ${ R \mathrm{(\AA)}}$  ')

pframe.write_message('MPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
#
app.MainLoop()


