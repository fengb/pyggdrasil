import wx
import wx.lib.newevent
import yaml

import pyggdrasil


TreeChangedEvent, EVT_TREE_CHANGED_EVENT = wx.lib.newevent.NewEvent()


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

        box = wx.BoxSizer(wx.HORIZONTAL)

        self.tree = Tree(root, self)
        box.Add(self.tree, 0, wx.EXPAND)

        self.graph = Graph(root, 40, 5, self)
        box.Add(self.graph, 1, wx.EXPAND)

        self.SetSizer(box)

        self.tree.Bind(EVT_TREE_CHANGED_EVENT, self.OnTreeChange)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelected)

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
                frame = Main(root, filename, self.GetParent(), wx.ID_ANY)
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
            if '.' not in filename:
                filename += '.pyg'
            self.filename = filename
            self._Save()

    def _Save(self):
        file = open(self.filename, 'w')
        try:
            yaml.dump(self.root.raw(), file)
        finally:
            file.close()

    def OnTreeChange(self, event):
        self.graph.Refresh()

    def OnItemSelected(self, event):
        self.graph.selected = self.tree.selected


class Graph(wx.ScrolledWindow):
    def __init__(self, root, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding
        self._selected = None

        self.root = root
        self.Refresh()
        self.Bind(wx.EVT_PAINT, self.Redraw)

    def getselected(self):
        return self._selected
    def setselected(self, value):
        if self._selected:
            # Restore previous selected
            self.DrawNode(self._selected)

        self._selected = value

        if value:
            self.DrawNode(value, bgcolor='#FFFF80')
    selected = property(getselected, setselected)

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

        for node in self.nodes:
            self.DrawNode(node, dc)

        dc.EndDrawing()

    def DrawNode(self, node, dc=None, bgcolor=None):
        if dc == None:
            dc = wx.PaintDC(self)
            self.DoPrepareDC(dc)
            enddrawing = True
        else:
            enddrawing = False

        if bgcolor:
            dc.SetBrush(wx.Brush(bgcolor))

        pos = self.nodes[node]
        dc.DrawCircle(pos.real, pos.imag, self.radius)

        w, h = dc.GetTextExtent(node.id)
        dc.DrawText(node.id, pos.real - w/2.0, pos.imag - h/2.0)

        if enddrawing:
            dc.EndDrawing()


class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        box = wx.BoxSizer(wx.VERTICAL)

        self.tree = wx.TreeCtrl(self, wx.ID_ANY,
                                style=(wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS))
        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        box.Add(self.tree, 1, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(hbox, 0, wx.EXPAND)

        self.childinput = wx.TextCtrl(self, wx.ID_ANY)
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

    @property
    def selected(self):
        '''Return the selected node'''
        return self.nodes[self.tree.GetSelection()]

    def Refresh(self):
        self.tree.DeleteAllItems()
        self.nodes = pyggdrasil.model.EqualsDict()
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

        wx.PostEvent(self, TreeChangedEvent())

    def OnAdd(self, event):
        selectedid = self.tree.GetSelection()
        nodeid = self.childinput.GetValue()

        if nodeid:
            node = pyggdrasil.model.Node(str(nodeid), None, self.nodes[selectedid])

            newid = self.tree.AppendItem(selectedid, nodeid)
            self.nodes[newid] = node
            self.tree.Expand(selectedid)

            self.childinput.Clear()

            wx.PostEvent(self, TreeChangedEvent())

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        selectedid = self.tree.GetSelection()

        self.nodes[selectedid].parent = None
        del self.nodes[selectedid]

        self.tree.Delete(selectedid)

        wx.PostEvent(self, TreeChangedEvent())

    def OnBeginDrag(self, event):
        self._dragitem = event.GetItem()
        if self._dragitem.IsOk():
            event.Allow()

    def OnEndDrag(self, event):
        #TODO: Deal with children somehow
        parent = event.GetItem()

        if not parent.IsOk():
            return
        if parent == self.tree.GetItemParent(self._dragitem):
            return
        try:
            oldid = self._dragitem
        except AttributeError:
            return

        text = self.tree.GetItemText(oldid)
        self.tree.Delete(oldid)
        newid = self.tree.AppendItem(parent, text)
        self.tree.Expand(parent)

        node = self.nodes.pop(oldid)
        self.nodes[newid] = node
        node.parent = self.nodes[parent]

        wx.PostEvent(self, TreeChangedEvent())


class App(wx.App):
    def OnInit(self):
        root = pyggdrasil.model.Node('root', None)
        frame = Main(root, parent=None, id=wx.ID_ANY)
        frame.Show(True)
        return True
