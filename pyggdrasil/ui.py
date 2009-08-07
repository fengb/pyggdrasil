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
        self.graph = Graph(pyggdrasil.graph.generate(root), 30, 5, nb)
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
        self.SetScrollRate(1, 1)

        self.graph = graph
        self.radius = radius
        self.padding = padding

        self.Bind(wx.EVT_PAINT, self.Redraw)

    def getgraph(self):
        return self._graph

    def setgraph(self, graph):
        self._graph = graph
        self.SetSize((graph.width, graph.height))

    graph = property(getgraph, setgraph)


    def Redraw(self, event=None):
        dc = wx.PaintDC(self)
        dc.Clear()

        nodes = dict((node, pos * 2 * (self.radius + self.padding))
                              for (node, pos) in self.graph)

        for node in nodes:
            if node.parent:
                np = nodes[node]
                pp = nodes[node.parent]
                dc.DrawLine(np.real, np.imag, pp.real, pp.imag)

        for (node, pos) in nodes.items():
            dc.DrawCircle(pos.real, pos.imag, self.radius)
            dc.DrawText(node.id, pos.real, pos.imag)

        dc.EndDrawing()


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, None, -1, 'Pyggdrasil - new')
        frame.Show(True)
        return True
