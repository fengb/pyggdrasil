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


class EqualsDict(object):
    """Data structure to emulate a dict.

    Allow the use of non-hashables as key but performance is very slow.
    """
    def __init__(self):
        self._items = []

    def __getitem__(self, key):
        for item in self._items:
            if key == item[0]:
                return item[1]

        raise KeyError(key)

    def __setitem__(self, key, value):
        for item in self._items:
            if key == item[0]:
                item[1] = value
                break
        else:
            self._items.append([key, value])

    def __delitem__(self, key):
        for (i, item) in enumerate(self._items):
            if key == item[0]:
                self._items.pop(i)
                break

class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        box = wx.BoxSizer(wx.VERTICAL)

        self.tree = wx.TreeCtrl(self, -1,
                                style=(wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS))
        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
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
        self.Refresh()

    def Refresh(self):
        self.tree.DeleteAllItems()
        self.nodes = EqualsDict()
        self._PopulateTreeItem(self.root, None)

    def _PopulateTreeItem(self, node, parent):
        if parent:
            treeitem = self.tree.AppendItem(parent, node.id)
        else:
            treeitem = self.tree.AddRoot(node.id)
        self.nodes[treeitem] = node

        for child in node.children:
            self._PopulateTreeItem(child, treeitem)

    def OnRename(self, event):
        selectedid = self.tree.GetSelection()
        nodeid = event.GetLabel()
        self.nodes[selectedid].id = str(nodeid)

    def OnAdd(self, event):
        selectedid = self.tree.GetSelection()
        nodeid = self.childinput.GetValue()

        if nodeid:
            node = pyggdrasil.model.Node(str(nodeid), None, self.nodes[selectedid])

            newid = self.tree.AppendItem(selectedid, nodeid)
            self.nodes[newid] = node
            self.tree.Expand(selectedid)

            self.childinput.Clear()

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        selectedid = self.tree.GetSelection()

        self.nodes[selectedid].parent = None
        del self.nodes[selectedid]

        self.tree.Delete(selectedid)

    def OnBeginDrag(self, event):
        self._dragitem = event.GetItem()
        if self._dragitem.IsOk():
            event.Allow()

    def OnEndDrag(self, event):
        #TODO: Deal with children somehow
        if not event.GetItem().IsOk():
            return
        try:
            old = self._dragitem
        except AttributeError:
            return

        parent = event.GetItem()
        text = self.tree.GetItemText(old)
        self.tree.Delete(old)
        self.tree.AppendItem(parent, text)
        self.tree.Expand(parent)


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, parent=None, id=-1)
        frame.Show(True)
        return True
