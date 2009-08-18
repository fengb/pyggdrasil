import wx
import wx.lib.newevent
import math
import cmath
import yaml

import pyggdrasil


TreeChangedEvent, TREE_CHANGED_EVENT = wx.lib.newevent.NewEvent()
GraphSelectedEvent, GRAPH_SELECTED_EVENT = wx.lib.newevent.NewEvent()


class Main(wx.Frame):
    def __init__(self, root=None, filename=None, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.root = root or pyggdrasil.model.Node('root', None)
        self.filename = filename

        menubar = wx.MenuBar()

        file = wx.Menu()
        new = file.Append(wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnNew, new)
        open = file.Append(wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnOpen, open)
        file.AppendSeparator()

        close = file.Append(wx.ID_CLOSE, 'Close\tCtrl-W')
        self.Bind(wx.EVT_MENU, self.OnClose, close)
        save = file.Append(wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        saveas = file.Append(wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveas)
        file.AppendSeparator()

        file.Append(wx.ID_EXIT)
        menubar.Append(file, '&File')

        self.SetMenuBar(menubar)

        box = wx.BoxSizer(wx.HORIZONTAL)

        self._tree = Tree(self.root, self)
        box.Add(self._tree, 0, wx.EXPAND)

        self.graph = Graph(self.root, 40, 5, self)
        box.Add(self.graph, 1, wx.EXPAND)

        self.SetSizer(box)

        self._tree.Bind(TREE_CHANGED_EVENT, self.OnTreeChange)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelected)
        self.graph.Bind(GRAPH_SELECTED_EVENT, self.OnGraphSelected)

    def getfilename(self):
        return self._filename
    def setfilename(self, value):
        self._filename = value
        self.SetTitle('Pyggdrasil - ' + (self.filename or 'new'))
    filename = property(getfilename, setfilename)

    def OnNew(self, event):
        frame = Main(parent=self.GetParent(), id=wx.ID_ANY)
        frame.Show(True)

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

    def OnClose(self, event):
        self.Close()

    def OnTreeChange(self, event):
        self.graph.Refresh()

    def OnTreeSelected(self, event):
        self.graph.selected = self._tree.selected

    def OnGraphSelected(self, event):
        self._tree.selected = event.target


class Graph(wx.ScrolledWindow):
    def __init__(self, root, radius, padding, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.radius = radius
        self.padding = padding
        self._selected = None


        self.root = root
        self.Refresh()
        self.Bind(wx.EVT_PAINT, self.Redraw)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)

    def getselected(self):
        return self._selected
    def setselected(self, value):
        if self._selected:
            # Restore previous selected
            self.DrawNode(self._selected)

        self._selected = value

        if self._selected:
            self.DrawNode(self._selected, bgcolor='#FFFF80')
    selected = property(getselected, setselected)

    def Refresh(self):
        self.selected = None
        graph = pyggdrasil.graph.generate(self.root)

        scalar = 2 * (self.radius + self.padding)
        self.nodes = dict((node, pos * scalar)
                                     for (node, pos) in graph)

        pos = self.GetViewStart()
        self.SetScrollbars(1, 1, graph.width * scalar, graph.height * scalar)
        self.Scroll(*pos)

    def Redraw(self, event=None):
        dc = wx.PaintDC(self)
        self.DoPrepareDC(dc)
        dc.Clear()

        lines = []
        for node in self.nodes:
            if node.parent:
                npos = self.nodes[node]
                ppos = self.nodes[node.parent]
                vector = ppos - npos
                magnitude = abs(vector)
                direction = math.atan2(vector.imag, vector.real)

                # Adjust for the circles
                ppos -= self.radius * cmath.exp(direction * 1j)
                npos += self.radius * cmath.exp(direction * 1j)

                # Relational line
                lines.append((npos.real, npos.imag, ppos.real, ppos.imag))

                # Little arrow at the end
                pos1 = ppos - self.padding * cmath.exp((direction + 0.5) * 1j)
                pos2 = ppos - self.padding * cmath.exp((direction - 0.5) * 1j)
                lines.append((pos1.real, pos1.imag, ppos.real, ppos.imag))
                lines.append((pos2.real, pos2.imag, ppos.real, ppos.imag))

        if lines:
            dc.DrawLineList(lines)

        for node in self.nodes:
            self.DrawNode(node, dc)

        if self.selected:
            self.DrawNode(self.selected, dc=dc, bgcolor='#FFFF80')

        dc.EndDrawing()

    def DrawNode(self, node, dc=None, bgcolor=None):
        if dc == None:
            dc = wx.ClientDC(self)
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

    def OnMouseClick(self, event):
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        click = tuple(event.GetLogicalPosition(dc))

        for (node, pos) in self.nodes.items():
            if (pos.real - self.radius) <= click[0] <= (pos.real + self.radius) and \
               (pos.imag - self.radius) <= click[1] <= (pos.imag + self.radius):
                wx.PostEvent(self, GraphSelectedEvent(target=node))
                return


class Tree(wx.Panel):
    def __init__(self, root, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._tree = wx.TreeCtrl(self, wx.ID_ANY,
                                style=(wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS))
        self._tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)
        self._tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self._tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        sizer.Add(self._tree, 1, wx.EXPAND)

        sizer.Add(self._buttoncontrols())

        self.SetSizer(sizer)

        self.root = root
        self.Refresh()

    def _buttoncontrols(self):
        sizer = wx.FlexGridSizer(rows=0, cols=2)

        self._childinput = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self._childinput.Bind(wx.EVT_TEXT_ENTER, self.OnAdd)
        sizer.Add(self._childinput, 1, wx.EXPAND)

        add = wx.Button(self, wx.ID_ADD, 'Add Child')
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        sizer.Add(add, 1, wx.EXPAND)

        sizer.AddStretchSpacer()

        remove = wx.Button(self, wx.ID_REMOVE)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        sizer.Add(remove, 1, wx.EXPAND)

        sort = wx.Button(self, wx.ID_ANY, 'Sort')
        sort.Bind(wx.EVT_BUTTON, self.OnSort)
        sizer.Add(sort, 1, wx.EXPAND)

        self._autosort = wx.CheckBox(self, wx.ID_ANY, 'Auto Sort')
        self._autosort.Bind(wx.EVT_CHECKBOX, self.OnSort)
        sizer.Add(self._autosort)

        return sizer

    def getselected(self):
        return self.nodes[self._tree.GetSelection()]
    def setselected(self, value):
        item = self.nodes.getkey(value)
        self._tree.SelectItem(item)
    selected = property(getselected, setselected)

    @property
    def autosort(self):
        return self._autosort.IsChecked()

    def Refresh(self):
        self._tree.DeleteAllItems()
        self.nodes = pyggdrasil.model.EqualsDict()
        self._PopulateTreeItem(self.root, None)

    def _PopulateTreeItem(self, node, parent):
        if parent:
            treeitem = self._tree.AppendItem(parent, node.id)
        else:
            treeitem = self._tree.AddRoot(node.id)
        self.nodes[treeitem] = node

        for child in node.children:
            self._PopulateTreeItem(child, treeitem)

    def _SortItem(self, item):
        self._tree.SortChildren(item)
        self.nodes[item].sort()

        # I want an iterator
        child = self._tree.GetFirstChild(item)[0]
        while child.IsOk():
            self._SortItem(child)
            child = self._tree.GetNextSibling(child)

    def OnSort(self, event):
        self._SortItem(self._tree.GetRootItem())
        wx.PostEvent(self, TreeChangedEvent())

    def OnRename(self, event):
        selectedid = self._tree.GetSelection()
        nodeid = event.GetLabel()
        self.nodes[selectedid].id = str(nodeid)

        wx.PostEvent(self, TreeChangedEvent())

    def OnAdd(self, event):
        selectedid = self._tree.GetSelection()
        nodeid = self._childinput.GetValue()

        if nodeid:
            node = pyggdrasil.model.Node(str(nodeid), None, self.nodes[selectedid])

            newid = self._tree.AppendItem(selectedid, nodeid)
            self.nodes[newid] = node
            self._tree.Expand(selectedid)

            self._childinput.Clear()

            if self.autosort:
                self._SortItem(selectedid)
            wx.PostEvent(self, TreeChangedEvent())

    def OnRemove(self, event):
        #TODO: Deal with children somehow
        selectedid = self._tree.GetSelection()

        # Do not let root node get removed
        if self.nodes[selectedid].parent:
            self.nodes[selectedid].parent = None
            del self.nodes[selectedid]

            self._tree.Delete(selectedid)

            wx.PostEvent(self, TreeChangedEvent())

    def OnBeginDrag(self, event):
        self._dragitem = event.GetItem()
        if self._dragitem.IsOk():
            event.Allow()

    def OnEndDrag(self, event):
        parent = event.GetItem()

        if not parent.IsOk():
            return
        if parent == self._tree.GetItemParent(self._dragitem):
            return
        try:
            oldid = self._dragitem
        except AttributeError:
            return

        text = self._tree.GetItemText(oldid)
        self._tree.Delete(oldid)

        node = self.nodes.pop(oldid)
        node.parent = self.nodes[parent]
        self._PopulateTreeItem(node, parent)
        self._tree.Expand(parent)

        wx.PostEvent(self, TreeChangedEvent())


class App(wx.App):
    def OnInit(self):
        self.SetAppName('Pyggdrasil')
        root = pyggdrasil.model.Node('root', None)
        frame = Main(parent=None, id=wx.ID_ANY)
        frame.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
        frame.Show(True)
        return True

    def OnMenuExit(self, event):
        self.ExitMainLoop()
