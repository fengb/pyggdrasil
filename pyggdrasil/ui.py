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
        self.graph = Graph(root, 40, 5, nb)
        self.tree = Tree(root, nb)
        nb.AddPage(self.graph, 'Visualize')
        nb.AddPage(self.tree, 'Tree')
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
    def __init__(self, root, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding

        graph = pyggdrasil.graph.generate(root)

        scalar = 2 * (self.radius + self.padding)
        self.nodes = dict((node, pos * scalar)
                              for (node, pos) in graph)
        self.SetScrollbars(1, 1, graph.width * scalar, graph.height * scalar)

        self.Bind(wx.EVT_PAINT, self.Redraw)

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


class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        box = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(self, -1)
        box.Add(self.tree, 1, wx.EXPAND)

        self.SetSizer(box)

        self._AddItem(root, None)

    def _AddItem(self, node, parent):
        if parent:
            treeitem = self.tree.AppendItem(parent, node.id)
        else:
            treeitem = self.tree.AddRoot(node.id)
        for child in node.children:
            self._AddItem(child, treeitem)


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, None, -1, 'Pyggdrasil - new')
        frame.Show(True)
        return True
