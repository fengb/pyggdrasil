import wx
import yaml

import pyggdrasil


class Main(wx.Frame):
    def __init__(self, root=None, filename=None, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.root = root
        self.filename = filename

        menubar = wx.MenuBar()

        file = wx.Menu()
        file.Append(wx.ID_OPEN)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpen)
        file.Append(wx.ID_SAVE)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSave)
        file.Append(wx.ID_SAVEAS)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveAs)
        menubar.Append(file, '&File')

        self.SetMenuBar(menubar)

        notebook = wx.Notebook(self, -1)
        self.graph = Graph(root, 40, 5, notebook)
        notebook.AddPage(self.graph, 'Visualize')
        self.tree = Tree(root, notebook)
        notebook.AddPage(self.tree, 'Tree')
        self.graph.SetFocus()

    def getfilename(self):
        return self._filename
    def setfilename(self, value):
        self._filename = value
        self.SetTitle('Pyggdrasil - ' + (self.filename or 'new'))
    filename = property(getfilename, setfilename)

    def OnOpen(self, event):
        filename = wx.LoadFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            file = open(filename)
            try:
                root = pyggdrasil.model.Node.from_raw(yaml.load(file))
                frame = Main(root, filename, self.GetParent(), -1)
                frame.Show(True)
            finally:
                file.close()

    def OnSave(self, event):
        if self.filename:
            self._Save()
        else:
            self.OnSaveAs(event)

    def OnSaveAs(self, event):
        filename = wx.SaveFileSelector('Pyggdrasil', extension='pyg', parent=self)
        if filename:
            self.filename = filename
            self._Save()

    def _Save(self):
        file = open(self.filename, 'w')
        try:
            yaml.dump(self.root.raw(), file)
        finally:
            file.close()


class Graph(wx.ScrolledWindow):
    def __init__(self, root, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding

        self.root = root
        self.Refresh()
        self.Bind(wx.EVT_PAINT, self.Redraw)

    def Refresh(self):
        graph = pyggdrasil.graph.generate(self.root)

        scalar = 2 * (self.radius + self.padding)
        self.nodes = dict((node, pos * scalar)
                              for (node, pos) in graph)
        self.SetScrollbars(1, 1, graph.width * scalar, graph.height * scalar)

    def Redraw(self, event=None):
        dc = wx.PaintDC(self)
        self.DoPrepareDC(dc)
        dc.Clear()

        for node in self.nodes:
            if node.parent:
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

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(hbox, 0, wx.EXPAND)

        self.childinput = wx.TextCtrl(self, -1)
        hbox.Add(self.childinput)

        add = wx.Button(self, wx.ID_ADD, 'Add Child')
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=wx.ID_ADD)
        hbox.Add(add, 0)

        hbox.AddStretchSpacer()

        remove = wx.Button(self, wx.ID_REMOVE)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, id=wx.ID_REMOVE)
        hbox.Add(remove)

        self.SetSizer(box)

        self.root = root
        self.nodes = dict((node.id, node) for node in self.root.unroll())
        self.Refresh()

    def Refresh(self):
        self.tree.DeleteAllItems()
        self._PopulateTree(self.root, None)

    def _PopulateTree(self, node, parent):
        if parent:
            treeitem = self.tree.AppendItem(parent, node.id)
        else:
            treeitem = self.tree.AddRoot(node.id)
        for child in node.children:
            self._PopulateTree(child, treeitem)

    def OnAdd(self, event):
        treeid = self.tree.GetSelection()
        nodeid = self.childinput.GetValue()

        parentid = self.tree.GetItemText(treeid)
        node = pyggdrasil.model.Node(nodeid, None, self.nodes[parentid])

        self.tree.AppendItem(treeid, nodeid)
        self.tree.Expand(treeid)

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        treeid = self.tree.GetSelection()

        nodeid = self.tree.GetItemText(treeid)
        self.nodes[nodeid].parent = None
        del self.nodes[nodeid]

        self.tree.Delete(treeid)


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, parent=None, id=-1)
        frame.Show(True)
        return True
