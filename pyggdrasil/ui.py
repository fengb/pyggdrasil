import wx
import yaml

import pyggdrasil


class Main(wx.Frame):
    def __init__(self, root, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        menubar = wx.MenuBar()

        file = wx.Menu()
        file.Append(102, '&Open')
        wx.EVT_MENU(self, 102, self.OnOpen)
        menubar.Append(file, '&File')

        self.SetMenuBar(menubar)

        nb = wx.Notebook(self, -1)
        self.graph = Graph(pyggdrasil.graph.generate(root), 40, 5, nb)
        self.graph.Redraw()
        nb.AddPage(self.graph, 'Visualize')
        self.graph.SetFocus()

    def OnOpen(self, event):
        filename = wx.LoadFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            file = open(filename)
            try:
                root = pyggdrasil.model.Node.from_raw(yaml.load(file))
                frame = Main(root, self.GetParent(), -1, 'Pyggdrasil - ' + filename)
                frame.Show(True)
            finally:
                file.close()


class Graph(wx.ScrolledWindow):
    def __init__(self, graph, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding
        self.graph = graph

        self.Bind(wx.EVT_PAINT, self.Redraw)

    def getgraph(self):
        return self._graph

    def setgraph(self, graph):
        self._graph = graph

        scalar = 2 * (self.radius + self.padding)
        self.nodes = dict((node, pos * scalar)
                              for (node, pos) in self.graph)

        self.SetScrollbars(1, 1, graph.width * scalar, graph.height * scalar)

    graph = property(getgraph, setgraph)


    def Redraw(self, event=None):
        dc = wx.PaintDC(self)
        self.DoPrepareDC(dc)
        dc.Clear()

        for node in self.nodes:
            if node.parent:
                # Offset to draw line ending at top edge
                npos = self.nodes[node]
                ppos = self.nodes[node.parent]

                dc.DrawLine(npos.real, npos.imag, ppos.real, ppos.imag)

        for (node, pos) in self.nodes.items():
            dc.DrawCircle(pos.real, pos.imag, self.radius)

            w, h = dc.GetTextExtent(node.id)
            dc.DrawText(node.id, pos.real - w/2.0, pos.imag - h/2.0)

        dc.EndDrawing()


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, None, -1, 'Pyggdrasil - new')
        frame.Show(True)
        return True
